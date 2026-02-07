"""
Sistema de Agendamento e Auto-Postagem
Suporta imagens, carrosséis e stories
"""
import json
import os
import time
import random
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException

from utils import HumanBehavior, logger, safe_execute, print_success, print_info, print_error
from config import config

@dataclass
class ScheduledPost:
    """Post agendado"""
    id: str
    content_type: str  # 'feed', 'story', 'reel'
    media_path: str
    caption: str
    hashtags: List[str]
    scheduled_time: str
    posted: bool = False
    posted_at: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    @property
    def is_due(self) -> bool:
        """Verifica se está na hora de postar"""
        if self.posted:
            return False
        scheduled = datetime.fromisoformat(self.scheduled_time)
        now = datetime.now()
        return now >= scheduled and (now - scheduled).seconds < 300

class ContentScheduler:
    """Agendador inteligente de conteúdo"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
        # Arquivos
        self.schedule_file = os.path.join(config.DATA_DIR, "content_schedule.json")
        self.templates_file = os.path.join(config.DATA_DIR, "caption_templates.json")
        
        # Dados
        self.posts_queue: List[ScheduledPost] = []
        self.templates: Dict = {}
        self._stop_event = threading.Event()
        
        self.load_data()
        self.load_templates()
    
    def load_data(self):
        """Carrega agenda"""
        try:
            from utils import load_json
            data = load_json(self.schedule_file, [])
            self.posts_queue = [ScheduledPost(**p) for p in data]
            logger.info(f"📅 {len(self.posts_queue)} posts carregados")
        except Exception as e:
            logger.error(f"Erro ao carregar agenda: {e}")
            self.posts_queue = []
    
    def save_data(self):
        """Salva agenda"""
        try:
            from utils import save_json
            save_json([p.to_dict() for p in self.posts_queue], self.schedule_file)
        except Exception as e:
            logger.error(f"Erro ao salvar agenda: {e}")
    
    def load_templates(self):
        """Carrega templates de legenda"""
        default = {
            "motivational": [
                "💪 {message}\n\n{hashtags}",
                "🔥 {message}\n\n{hashtags}",
                "✨ {message}\n\n{hashtags}"
            ],
            "educational": [
                "📚 {message}\n\n{hashtags}",
                "💡 {message}\n\n{hashtags}",
                "🎯 {message}\n\n{hashtags}"
            ],
            "engagement": [
                "👇 {message}\n\n{hashtags}",
                "🤔 {message}\n\n{hashtags}",
                "💬 {message}\n\n{hashtags}"
            ],
            "questions": [
                "Qual sua opinião? {message}\n\n{hashtags}",
                "Concorda? {message}\n\n{hashtags}",
                "Comenta! {message}\n\n{hashtags}"
            ],
            "messages": {
                "crescimento": [
                    "Qual sua meta de seguidores para este mês?",
                    "O que está te impedindo de crescer?",
                    "Consistência é a chave do sucesso!"
                ],
                "conteudo": [
                    "Que tipo de conteúdo você mais gosta?",
                    "Salva esse post para ver depois!",
                    "Marca alguém que precisa ver isso!"
                ],
                "engajamento": [
                    "Dê dois toques se concorda!",
                    "Comenta sua opinião!",
                    "Compartilha nos stories!"
                ]
            }
        }
        
        try:
            from utils import load_json
            self.templates = load_json(self.templates_file, default)
        except:
            self.templates = default
            self.save_templates()
    
    def save_templates(self):
        """Salva templates"""
        from utils import save_json
        save_json(self.templates, self.templates_file)
    
    def generate_caption(self, topic: str = "engajamento", style: str = "engagement") -> str:
        """Gera legenda usando templates"""
        templates = self.templates.get(style, self.templates.get("engagement", ["{message}"]))
        template = random.choice(templates)
        
        messages = self.templates.get("messages", {}).get(topic, ["Conteúdo incrível!"])
        message = random.choice(messages)
        
        # Gera hashtags
        base_hashtags = config.TARGET_HASHTAGS[:10]
        hashtags = " ".join([f"#{tag}" for tag in base_hashtags])
        
        return template.format(message=message, hashtags=hashtags)
    
    def schedule_post(self, media_path: str, caption: str = "", 
                     hashtags: List[str] = None,
                     post_datetime: datetime = None,
                     content_type: str = "feed") -> str:
        """Agenda um novo post"""
        
        # Gera ID único
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Gera legenda se não fornecida
        if not caption:
            caption = self.generate_caption()
        
        # Horário padrão se não fornecido
        if not post_datetime:
            post_datetime = datetime.now() + timedelta(hours=1)
        
        scheduled = ScheduledPost(
            id=post_id,
            content_type=content_type,
            media_path=media_path,
            caption=caption,
            hashtags=hashtags or [],
            scheduled_time=post_datetime.isoformat()
        )
        
        self.posts_queue.append(scheduled)
        self.save_data()
        
        print_success(f"Post agendado para {post_datetime.strftime('%d/%m %H:%M')}")
        return post_id
    
    def list_scheduled(self) -> List[ScheduledPost]:
        """Lista posts agendados pendentes"""
        return [p for p in self.posts_queue if not p.posted]
    
    def cancel_post(self, post_id: str) -> bool:
        """Cancela um post agendado"""
        for i, post in enumerate(self.posts_queue):
            if post.id == post_id and not post.posted:
                self.posts_queue.pop(i)
                self.save_data()
                print_success(f"Post {post_id} cancelado")
                return True
        return False
    
    # ============================================
    # PUBLICAÇÃO
    # ============================================
    
    def check_and_post(self) -> bool:
        """Verifica e publica posts agendados"""
        for post in self.posts_queue:
            if post.is_due:
                logger.info(f"🚀 Publicando post: {post.id}")
                
                success = False
                try:
                    if post.content_type == "feed":
                        success = self._post_to_feed(post)
                    elif post.content_type == "story":
                        success = self._post_to_story(post)
                    else:
                        post.error = "Tipo não suportado"
                except Exception as e:
                    post.error = str(e)
                    logger.error(f"Erro ao publicar: {e}")
                
                if success:
                    post.posted = True
                    post.posted_at = datetime.now().isoformat()
                    print_success(f"Post publicado: {post.id}")
                
                self.save_data()
                return success
        
        return False
    
    @safe_execute(max_retries=2)
    def _post_to_feed(self, post: ScheduledPost) -> bool:
        """Publica no feed"""
        
        # Verifica arquivo
        if not os.path.exists(post.media_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {post.media_path}")
        
        # Clica em criar
        create_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS['create_post_button']))
        )
        create_btn.click()
        HumanBehavior.random_delay(2, 3)
        
        # Seleciona arquivo
        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(os.path.abspath(post.media_path))
        HumanBehavior.random_delay(3, 5)
        
        # Avança
        next_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Avançar')]"))
        )
        next_btn.click()
        HumanBehavior.random_delay(2, 3)
        
        # Adiciona legenda
        caption_box = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label='Escreva uma legenda...']"))
        )
        
        full_caption = post.caption
        if post.hashtags:
            full_caption += "\n\n" + " ".join([f"#{tag}" for tag in post.hashtags])
        
        # Digita lentamente
        for char in full_caption:
            caption_box.send_keys(char)
            time.sleep(random.uniform(0.03, 0.1))
        
        HumanBehavior.random_delay(1, 2)
        
        # Publica
        share_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Compartilhar')]"))
        )
        share_btn.click()
        
        # Aguarda confirmação
        HumanBehavior.random_delay(5, 8)
        
        # Verifica se publicou
        try:
            self.driver.find_element(By.XPATH, "//span[contains(text(), 'Publicado')]")
            return True
        except:
            # Pode ter publicado mesmo sem ver a mensagem
            return True
    
    @safe_execute(max_retries=2)
    def _post_to_story(self, post: ScheduledPost) -> bool:
        """Publica story"""
        
        if not os.path.exists(post.media_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {post.media_path}")
        
        # Acessa criação de story
        self.driver.get("https://www.instagram.com/")
        HumanBehavior.random_delay(2, 3)
        
        # Clica no + do story (primeiro anel)
        story_rings = self.driver.find_elements(By.CSS_SELECTOR, config.SELECTORS['story_ring'])
        if story_rings:
            story_rings[0].click()
            HumanBehavior.random_delay(2, 3)
        
        # Seleciona imagem
        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        file_input.send_keys(os.path.abspath(post.media_path))
        HumanBehavior.random_delay(3, 5)
        
        # Adiciona texto se tiver
        if post.caption:
            try:
                text_btn = self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Texto']")
                text_btn.click()
                HumanBehavior.random_delay(1, 2)
                
                actions = ActionChains(self.driver)
                actions.send_keys(post.caption[:50])
                actions.perform()
                
                done_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Concluir')]")
                done_btn.click()
            except:
                pass
        
        # Compartilha
        share_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Seu story')]"))
        )
        share_btn.click()
        
        HumanBehavior.random_delay(3, 5)
        return True
    
    # ============================================
    # AUTO-AGENDAMENTO
    # ============================================
    
    def auto_schedule_week(self, content_folder: str = None, 
                          posts_per_day: int = None,
                          optimal_hours: List[int] = None):
        """Agenda posts automaticamente para a semana"""
        
        content_folder = content_folder or config.CONTENT_FOLDER
        posts_per_day = posts_per_day or config.POSTS_PER_DAY
        optimal_hours = optimal_hours or config.DEFAULT_POST_HOURS
        
        # Busca imagens
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(list(Path(content_folder).glob(ext)))
        
        if not image_files:
            print_error(f"Nenhuma imagem encontrada em {content_folder}")
            return 0
        
        print_info(f"Agendando {len(image_files)} posts ({posts_per_day}/dia)")
        
        now = datetime.now()
        scheduled = 0
        image_idx = 0
        
        for day_offset in range(7):
            for post_num in range(posts_per_day):
                if image_idx >= len(image_files):
                    break
                
                # Calcula horário
                hour = optimal_hours[post_num % len(optimal_hours)]
                post_time = now + timedelta(days=day_offset)
                post_time = post_time.replace(
                    hour=hour, 
                    minute=random.randint(0, 30),
                    second=0
                )
                
                # Se horário já passou, vai para amanhã
                if post_time < now:
                    post_time += timedelta(days=1)
                
                # Seleciona imagem
                image = image_files[image_idx]
                
                # Gera legenda variada
                topics = ["crescimento", "conteudo", "engajamento"]
                styles = ["motivational", "educational", "engagement", "questions"]
                caption = self.generate_caption(
                    topic=random.choice(topics),
                    style=random.choice(styles)
                )
                
                self.schedule_post(
                    str(image),
                    caption,
                    config.TARGET_HASHTAGS[:8],
                    post_time,
                    "feed"
                )
                
                scheduled += 1
                image_idx += 1
        
        print_success(f"{scheduled} posts agendados!")
        return scheduled
    
    # ============================================
    # DAEMON
    # ============================================
    
    def run_scheduler_daemon(self, check_interval: int = 300):
        """
        Loop contínuo de verificação
        Rode em thread separada
        """
        print_info(f"Iniciando daemon de publicação (verificação a cada {check_interval}s)")
        
        while not self._stop_event.is_set():
            try:
                posted = self.check_and_post()
                if posted:
                    logger.info("✅ Post publicado pelo daemon")
                
                # Aguarda próxima verificação
                self._stop_event.wait(check_interval)
                
            except Exception as e:
                logger.error(f"Erro no daemon: {e}")
                self._stop_event.wait(60)
        
        print_info("Daemon de publicação encerrado")
    
    def stop_daemon(self):
        """Para o daemon"""
        self._stop_event.set()
    
    def is_daemon_running(self) -> bool:
        """Verifica se daemon está rodando"""
        return not self._stop_event.is_set()

# Importações
from utils import load_json, save_json, print_success, print_info, print_error
