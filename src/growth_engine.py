"""
Motor de Crescimento Orgânico
Estratégias avançadas para aumentar seguidores
"""
import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from utils import HumanBehavior, RateLimiter, logger, safe_execute, print_success, print_info
from config import config

@dataclass
class GrowthStats:
    """Estatísticas de crescimento diário"""
    dia: str
    follows_realizados: int = 0
    unfollows_realizados: int = 0
    curtidas_enviadas: int = 0
    comentarios_enviados: int = 0
    stories_visualizados: int = 0
    posts_curtidos: int = 0
    
    def to_dict(self):
        return asdict(self)

class GrowthEngine:
    """Motor completo de crescimento orgânico"""
    
    def __init__(self, driver, wait, rate_limiter, followers_manager):
        self.driver = driver
        self.wait = wait
        self.rate_limiter = rate_limiter
        self.fm = followers_manager
        
        # Arquivos
        self.stats_file = os.path.join(config.DATA_DIR, "growth_stats.json")
        self.targets_file = os.path.join(config.DATA_DIR, "growth_targets.json")
        
        # Dados
        self.daily_stats: Dict[str, GrowthStats] = {}
        self.targets = self._load_targets()
        
        self._load_stats()
    
    def _load_stats(self):
        """Carrega estatísticas diárias"""
        try:
            from utils import load_json
            data = load_json(self.stats_file, {})
            self.daily_stats = {k: GrowthStats(**v) for k, v in data.items()}
        except:
            self.daily_stats = {}
    
    def _save_stats(self):
        """Salva estatísticas"""
        from utils import save_json
        save_json(
            {k: v.to_dict() for k, v in self.daily_stats.items()},
            self.stats_file
        )
    
    def _load_targets(self) -> Dict:
        """Carrega alvos de crescimento"""
        from utils import load_json
        default = {
            "influenciadores": [],
            "concorrentes": [],
            "hashtags_populares": config.TARGET_HASHTAGS,
            "comentarios_templates": [
                "Conteúdo incrível! 🔥",
                "Muito bom mesmo! 👏",
                "Adorei isso! ❤️",
                "Que post fantástico! ✨",
                "Valeu pela dica! 🙌",
                "Salvando aqui! 💾",
                "Muito útil, obrigado! 🙏"
            ]
        }
        return load_json(self.targets_file, default)
    
    def save_targets(self):
        """Salva alvos"""
        from utils import save_json
        save_json(self.targets, self.targets_file)
    
    def add_target_influencer(self, username: str, niche: str = ""):
        """Adiciona influenciador alvo"""
        username = username.strip().lower()
        if username not in [t.get("username") for t in self.targets["influenciadores"]]:
            self.targets["influenciadores"].append({
                "username": username,
                "niche": niche,
                "added_at": datetime.now().isoformat()
            })
            self.save_targets()
            print_success(f"Influenciador @{username} adicionado")
    
    def _get_today_stats(self) -> GrowthStats:
        """Retorna ou cria estatísticas de hoje"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_stats:
            self.daily_stats[today] = GrowthStats(dia=today)
        return self.daily_stats[today]
    
    # ============================================
    # ESTRATÉGIA 1: FOLLOW EM CURTIDORES
    # ============================================
    
    @safe_execute(max_retries=2)
    def follow_recent_likers(self, post_url: str, max_follows: int = 15) -> int:
        """
        ESTRATÉGIA POWER: Segue quem curtiu posts recentes
        Taxa de follow-back: 30-50%
        """
        print_info(f"Processando curtidas: {post_url[:50]}...")
        
        self.driver.get(post_url)
        HumanBehavior.long_delay()
        
        try:
            # Clica na contagem de curtidas
            likes_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.SELECTORS['likes_link']))
            )
            likes_link.click()
            HumanBehavior.random_delay(3, 5)
            
            # Container
            dialog = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS['dialog_container']))
            )
            
            followed = 0
            processed = set()
            
            while followed < max_follows:
                # Encontra botões de seguir
                follow_buttons = dialog.find_elements(
                    By.XPATH, "//button[contains(text(), 'Seguir') and not(contains(text(), 'Seguindo'))]"
                )
                
                for btn in follow_buttons:
                    if followed >= max_follows:
                        break
                    
                    try:
                        # Scroll até o botão
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        HumanBehavior.random_delay(0.5, 1)
                        
                        # Extrai username
                        try:
                            username_elem = btn.find_element(By.XPATH, "../..//span[@dir='auto']")
                            username = username_elem.text.strip()
                            
                            if username in processed or username in self.fm.followed_users:
                                continue
                            processed.add(username)
                        except:
                            username = f"user_{random.randint(1000,9999)}"
                        
                        btn.click()
                        followed += 1
                        
                        # Registra
                        self._get_today_stats().follows_realizados += 1
                        self.fm.followed_users[username] = type('obj', (object,), {
                            'username': username,
                            'followed_at': datetime.now().isoformat(),
                            'source': 'recent_liker'
                        })()
                        
                        self.rate_limiter.record_action('follows')
                        logger.info(f"✅ Seguiu curtidor {followed}/{max_follows}: @{username}")
                        
                        HumanBehavior.random_delay(8, 15)
                        
                    except Exception as e:
                        continue
                
                # Scroll para mais
                self.driver.execute_script("arguments[0].scrollTop += 600", dialog)
                HumanBehavior.scroll_pause()
                
                # Verifica se há mais
                new_buttons = dialog.find_elements(
                    By.XPATH, "//button[contains(text(), 'Seguir')]"
                )
                if len(new_buttons) <= len(processed):
                    break
            
            # Fecha
            try:
                self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Fechar']").click()
            except:
                pass
            
            self._save_stats()
            self.fm.save_data()
            
            print_success(f"{followed} curtidores seguidos!")
            return followed
            
        except Exception as e:
            logger.error(f"Erro na estratégia: {e}")
            return 0
    
    # ============================================
    # ESTRATÉGIA 2: STORY ENGAGEMENT
    # ============================================
    
    def mass_story_engagement(self, hashtags: List[str], max_stories: int = 50) -> int:
        """
        Visualiza stories de usuários do nicho
        Taxa de conversão: 5-10% visitam perfil
        """
        print_info(f"Visualizando stories: {max_stories} stories")
        
        viewed = 0
        
        for hashtag in hashtags[:3]:  # Máximo 3 hashtags
            if viewed >= max_stories:
                break
            
            try:
                self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
                HumanBehavior.random_delay(3, 5)
                
                # Clica no primeiro story
                story_ring = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS['story_ring']))
                )
                story_ring.click()
                HumanBehavior.random_delay(3, 5)
                
                while viewed < max_stories:
                    try:
                        time.sleep(random.uniform(2, 4))
                        
                        # Próximo story
                        next_btn = self.driver.find_element(
                            By.CSS_SELECTOR, "button._ac0d, div.coreSpriteRightChevron, button[aria-label='Próximo']"
                        )
                        next_btn.click()
                        viewed += 1
                        
                        self._get_today_stats().stories_visualizados += 1
                        
                    except:
                        break
                        
            except Exception as e:
                logger.warning(f"Sem stories para #{hashtag}: {e}")
                continue
        
        self._save_stats()
        print_success(f"{viewed} stories visualizados!")
        return viewed
    
    # ============================================
    # ESTRATÉGIA 3: COMENTÁRIOS ESTRATÉGICOS
    # ============================================
    
    def strategic_commenting(self, post_urls: List[str], max_comments: int = 10) -> int:
        """
        Comenta em posts de influenciadores grandes
        Exposição massiva = visitas ao perfil
        """
        print_info(f"Comentando estrategicamente: {max_comments} comentários")
        
        commented = 0
        templates = self.targets.get("comentarios_templates", ["👏", "🔥", "❤️"])
        
        for post_url in post_urls[:max_comments + 3]:  # Margem para erros
            if commented >= max_comments:
                break
            
            try:
                self.driver.get(post_url)
                HumanBehavior.long_delay()
                
                comment_text = random.choice(templates)
                
                # Clica na caixa de comentário
                comment_box = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS['comment_input']))
                )
                comment_box.click()
                HumanBehavior.random_delay(1, 2)
                
                # Digita
                for char in comment_text:
                    comment_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                HumanBehavior.random_delay(1, 2)
                
                # Envia
                submit_btn = self.driver.find_element(
                    By.XPATH, "//button[contains(text(), 'Publicar')]"
                )
                submit_btn.click()
                
                commented += 1
                self._get_today_stats().comentarios_enviados += 1
                
                logger.info(f"💬 Comentado: '{comment_text}'")
                HumanBehavior.random_delay(30, 60)  # Pausa longa
                
            except Exception as e:
                logger.error(f"Erro ao comentar: {e}")
                continue
        
        self._save_stats()
        print_success(f"{commented} comentários enviados!")
        return commented
    
    # ============================================
    # ESTRATÉGIA 4: LIKE EM HASHTAG
    # ============================================
    
    def like_by_hashtag(self, hashtag: str, max_likes: int = 30) -> int:
        """Curti posts de uma hashtag"""
        print_info(f"Curtindo posts de #{hashtag}")
        
        self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        HumanBehavior.long_delay()
        
        liked = 0
        
        try:
            # Coleta links de posts
            posts = self.driver.find_elements(By.CSS_SELECTOR, config.SELECTORS['post_links'])[:max_likes + 5]
            post_urls = [p.get_attribute('href') for p in posts if p.get_attribute('href')]
            
            for url in post_urls:
                if liked >= max_likes:
                    break
                
                if not self.rate_limiter.can_perform('likes', config.MAX_LIKES_PER_HOUR):
                    break
                
                try:
                    self.driver.get(url)
                    HumanBehavior.random_delay(2, 4)
                    
                    # Procura botão de curtir
                    like_btn = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS['like_button'])
                    like_btn.click()
                    
                    liked += 1
                    self._get_today_stats().curtidas_enviadas += 1
                    self.rate_limiter.record_action('likes')
                    
                    logger.info(f"❤️  Curtido {liked}/{max_likes}")
                    HumanBehavior.random_delay(3, 6)
                    
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Erro ao curtir: {e}")
        
        self._save_stats()
        print_success(f"{liked} posts curtidos em #{hashtag}!")
        return liked
    
    # ============================================
    # SESSÃO COMPLETA
    # ============================================
    
    def run_growth_session(self, session_type: str = "balanced"):
        """
        Executa sessão completa de crescimento
        
        session_type:
        - "aggressive": Máximo de ações (risco maior)
        - "balanced": Equilíbrio (recomendado)
        - "safe": Conservador (contas novas)
        """
        configs = {
            "aggressive": {
                "follows": 50, "unfollows": 50, "likes": 100, 
                "comments": 15, "stories": 100, "likes_per_tag": 50
            },
            "balanced": {
                "follows": 30, "unfollows": 30, "likes": 60,
                "comments": 8, "stories": 50, "likes_per_tag": 30
            },
            "safe": {
                "follows": 15, "unfollows": 15, "likes": 30,
                "comments": 3, "stories": 20, "likes_per_tag": 15
            }
        }
        
        cfg = configs.get(session_type, configs["balanced"])
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║  🚀 SESSÃO DE CRESCIMENTO: {session_type.upper():12}               ║
╠══════════════════════════════════════════════════════════╣
║  Follows: {cfg['follows']:3}  |  Unfollows: {cfg['unfollows']:3}                    ║
║  Likes:   {cfg['likes']:3}  |  Comments:   {cfg['comments']:3}                    ║
║  Stories: {cfg['stories']:3}                                          ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        # 1. UNFOLLOW PRIMEIRO
        print("\n📍 FASE 1: Limpando não-seguidores...")
        self.fm.clean_non_followers(cfg["unfollows"], days_before_unfollow=2)
        
        # 2. FOLLOW EM CURTIDORES
        print("\n📍 FASE 2: Follow em curtidores de influenciadores...")
        if self.targets["influenciadores"]:
            influencer = random.choice(self.targets["influenciadores"])
            post_url = self._get_recent_post(influencer["username"])
            if post_url:
                self.follow_recent_likers(post_url, cfg["follows"] // 2)
        
        # 3. FOLLOW EM SEGUIDORES DE CONCORRENTES
        remaining = cfg["follows"] - self._get_today_stats().follows_realizados
        if remaining > 0 and self.targets["concorrentes"]:
            print("\n📍 FASE 3: Follow em seguidores de concorrentes...")
            competitor = random.choice(self.targets["concorrentes"])
            self.fm.follow_followers_of_target(
                competitor if isinstance(competitor, str) else competitor["username"],
                max_follows=remaining
            )
        
        # 4. LIKE EM HASHTAGS
        print("\n📍 FASE 4: Curtindo posts de hashtags...")
        for hashtag in self.targets["hashtags_populares"][:2]:
            self.like_by_hashtag(hashtag, cfg["likes_per_tag"] // 2)
            HumanBehavior.random_delay(10, 20)
        
        # 5. STORY ENGAGEMENT
        print("\n📍 FASE 5: Visualizando stories...")
        self.mass_story_engagement(
            self.targets["hashtags_populares"][:3],
            cfg["stories"]
        )
        
        # 6. COMENTÁRIOS
        print("\n📍 FASE 6: Comentários estratégicos...")
        if self.targets["influenciadores"]:
            posts = []
            for inf in self.targets["influenciadores"][:2]:
                post = self._get_recent_post(inf["username"])
                if post:
                    posts.append(post)
            self.strategic_commenting(posts, cfg["comments"])
        
        # RELATÓRIO
        self._print_session_report()
    
    def _get_recent_post(self, username: str) -> Optional[str]:
        """Pega URL do post mais recente"""
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            HumanBehavior.random_delay(3, 5)
            
            post = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS['post_links'])
            return post.get_attribute('href')
        except:
            return None
    
    def _print_session_report(self):
        """Imprime relatório da sessão"""
        stats = self._get_today_stats()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           📊 RELATÓRIO DA SESSÃO                         ║
╠══════════════════════════════════════════════════════════╣
║  📅 Data: {stats.dia}                                    ║
║  ➕ Follows:      {stats.follows_realizados:4}                          ║
║  ➖ Unfollows:    {stats.unfollows_realizados:4}                          ║
║  ❤️  Curtidas:     {stats.curtidas_enviadas:4}                          ║
║  💬 Comentários:  {stats.comentarios_enviados:4}                          ║
║  👀 Stories:      {stats.stories_visualizados:4}                          ║
╠══════════════════════════════════════════════════════════╣
║  📈 Projeção: ~{stats.follows_realizados * 0.3:.0f} novos seguidores (30% conv.)  ║
╚══════════════════════════════════════════════════════════╝
        """
        print(report)
    
    def get_weekly_report(self) -> dict:
        """Relatório semanal"""
        week_ago = datetime.now() - timedelta(days=7)
        weekly = defaultdict(int)
        
        for date_str, stats in self.daily_stats.items():
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date >= week_ago:
                for key, value in vars(stats).items():
                    if isinstance(value, int):
                        weekly[key] += value
        
        return dict(weekly)

# Importações
from utils import load_json, save_json
