"""
Gerenciamento Avançado de Seguidores
- Seguir seguidores de perfis alvo
- Unfollow inteligente
- Whitelist de proteção
- Análise de follow-back
"""
import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import List, Set, Dict, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from utils import HumanBehavior, RateLimiter, logger, safe_execute
from config import config

@dataclass
class UserProfile:
    """Perfil de usuário seguido"""
    username: str
    user_id: str = ""
    followers_count: int = 0
    following_count: int = 0
    is_private: bool = False
    is_verified: bool = False
    followed_at: Optional[str] = None
    unfollowed_at: Optional[str] = None
    follows_back: Optional[bool] = None
    source: str = ""  # De onde veio (influencer, hashtag, etc)
    
    def to_dict(self):
        return asdict(self)
    
    @property
    def days_since_followed(self) -> int:
        """Dias desde que seguiu"""
        if not self.followed_at:
            return 0
        followed_date = datetime.fromisoformat(self.followed_at)
        return (datetime.now() - followed_date).days

class FollowersManager:
    """Gerenciador completo de seguidores"""
    
    def __init__(self, driver, wait, rate_limiter):
        self.driver = driver
        self.wait = wait
        self.rate_limiter = rate_limiter
        
        # Arquivos de dados
        self.data_file = os.path.join(config.DATA_DIR, "followers_data.json")
        self.whitelist_file = os.path.join(config.DATA_DIR, "whitelist.json")
        self.stats_file = os.path.join(config.DATA_DIR, "follower_stats.json")
        
        # Dados em memória
        self.followed_users: Dict[str, UserProfile] = {}
        self.whitelist: Set[str] = set()
        self.daily_stats = defaultdict(int)
        
        self.load_data()
    
    def load_data(self):
        """Carrega dados persistidos"""
        # Carrega usuários seguidos
        try:
            data = load_json(self.data_file, {})
            self.followed_users = {
                k: UserProfile(**v) for k, v in data.items()
            }
            logger.info(f"📂 Carregados {len(self.followed_users)} usuários do histórico")
        except Exception as e:
            logger.error(f"Erro ao carregar followers_data: {e}")
            self.followed_users = {}
        
        # Carrega whitelist
        try:
            self.whitelist = set(load_json(self.whitelist_file, []))
            logger.info(f"🛡️  Whitelist: {len(self.whitelist)} usuários protegidos")
        except Exception as e:
            logger.error(f"Erro ao carregar whitelist: {e}")
            self.whitelist = set()
        
        # Carrega estatísticas
        self.daily_stats = defaultdict(int, load_json(self.stats_file, {}))
    
    def save_data(self):
        """Persiste todos os dados"""
        try:
            save_json(
                {k: v.to_dict() for k, v in self.followed_users.items()},
                self.data_file
            )
            save_json(list(self.whitelist), self.whitelist_file)
            save_json(dict(self.daily_stats), self.stats_file)
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
    
    # ============================================
    # WHITELIST
    # ============================================
    
    def add_to_whitelist(self, username: str):
        """Adiciona usuário à whitelist"""
        username = username.lower().strip()
        self.whitelist.add(username)
        self.save_data()
        logger.info(f"🛡️  @{username} adicionado à whitelist")
    
    def remove_from_whitelist(self, username: str):
        """Remove usuário da whitelist"""
        username = username.lower().strip()
        self.whitelist.discard(username)
        self.save_data()
        logger.info(f"🗑️  @{username} removido da whitelist")
    
    def is_whitelisted(self, username: str) -> bool:
        """Verifica se usuário está na whitelist"""
        return username.lower().strip() in self.whitelist
    
    # ============================================
    # COLETA DE DADOS
    # ============================================
    
    def get_followers_list(self, username: str, max_followers: int = 100) -> List[str]:
        """Coleta lista de seguidores de um perfil"""
        logger.info(f"🔍 Coletando seguidores de @{username}...")
        
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            HumanBehavior.long_delay()
            
            # Clica em "Seguidores"
            followers_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.SELECTORS['followers_link']))
            )
            followers_btn.click()
            HumanBehavior.random_delay(3, 5)
            
            # Container da lista
            dialog = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS['dialog_container']))
            )
            
            followers = []
            last_count = 0
            scroll_attempts = 0
            max_scrolls = max_followers // 8 + 3
            
            while len(followers) < max_followers and scroll_attempts < max_scrolls:
                # Encontra usuários visíveis
                user_elements = dialog.find_elements(
                    By.CSS_SELECTOR, "span._aacl._aacs._aact"
                )
                
                for elem in user_elements:
                    username_text = elem.text.strip()
                    if username_text and username_text not in followers:
                        followers.append(username_text)
                        if len(followers) >= max_followers:
                            break
                
                # Scroll
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    dialog
                )
                HumanBehavior.scroll_pause()
                
                # Verifica se carregou mais
                if len(followers) == last_count:
                    scroll_attempts += 1
                else:
                    last_count = len(followers)
                    scroll_attempts = 0
            
            # Fecha dialog
            try:
                close_btn = self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Fechar']")
                close_btn.click()
            except:
                pass
            
            logger.info(f"✅ Coletados {len(followers)} seguidores de @{username}")
            return followers
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar seguidores: {e}")
            return []
    
    def get_following_list(self, max_following: int = 1000) -> List[str]:
        """Coleta lista de quem você segue"""
        logger.info(f"🔍 Coletando lista de seguindo...")
        
        try:
            # Vai para seu próprio perfil
            self.driver.get(f"https://www.instagram.com/{config.IG_USERNAME}/")
            HumanBehavior.long_delay()
            
            # Clica em "Seguindo"
            following_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.SELECTORS['following_link']))
            )
            following_btn.click()
            HumanBehavior.random_delay(3, 5)
            
            # Container
            dialog = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS['dialog_container']))
            )
            
            following = []
            last_count = 0
            no_change_count = 0
            
            while len(following) < max_following and no_change_count < 5:
                elements = dialog.find_elements(
                    By.CSS_SELECTOR, "span._aacl._aacs._aact"
                )
                
                for elem in elements:
                    username = elem.text.strip()
                    if username and username not in following:
                        following.append(username)
                
                # Scroll
                self.driver.execute_script(
                    "arguments[0].scrollTop += 800", 
                    dialog
                )
                HumanBehavior.scroll_pause()
                
                # Verifica se carregou mais
                if len(following) == last_count:
                    no_change_count += 1
                else:
                    last_count = len(following)
                    no_change_count = 0
            
            # Fecha dialog
            try:
                close_btn = self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Fechar']")
                close_btn.click()
            except:
                pass
            
            logger.info(f"✅ Coletados {len(following)} seguindo")
            return following
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar seguindo: {e}")
            return []
    
    def check_if_follows_back(self, username: str) -> bool:
        """Verifica se um usuário segue você de volta"""
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            HumanBehavior.random_delay(3, 5)
            
            # Procura indicadores de que segue você
            indicators = [
                "//button[contains(text(), 'Seguir de volta')]",
                "//span[contains(text(), 'Segue você')]",
                "//div[contains(text(), 'Segue você')]"
            ]
            
            for indicator in indicators:
                try:
                    self.driver.find_element(By.XPATH, indicator)
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar @{username}: {e}")
            return False
    
    # ============================================
    # AÇÕES
    # ============================================
    
    @safe_execute(max_retries=2)
    def follow_user(self, username: str, source: str = "") -> bool:
        """Segue um usuário específico"""
        if not self.rate_limiter.can_perform('follows', config.MAX_FOLLOWS_PER_HOUR):
            return False
        
        # Pula se já segue
        if username in self.followed_users and not self.followed_users[username].unfollowed_at:
            logger.info(f"⏭️  Já segue @{username}")
            return False
        
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            HumanBehavior.long_delay()
            
            # Verifica se é privado
            is_private = False
            try:
                self.driver.find_element(By.XPATH, "//span[contains(text(), 'Esta conta é privada')]")
                is_private = True
            except:
                pass
            
            # Clica em seguir
            follow_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.SELECTORS['follow_button']))
            )
            follow_btn.click()
            
            # Registra
            self.followed_users[username] = UserProfile(
                username=username,
                followed_at=datetime.now().isoformat(),
                is_private=is_private,
                source=source
            )
            
            self.rate_limiter.record_action('follows')
            self.daily_stats['follows_today'] += 1
            self.save_data()
            
            logger.info(f"✅ Seguiu @{username}")
            HumanBehavior.random_delay(8, 15)
            return True
            
        except TimeoutException:
            logger.info(f"⏭️  Já segue ou não encontrado: @{username}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao seguir @{username}: {e}")
            return False
    
    @safe_execute(max_retries=2)
    def unfollow_user(self, username: str, check_follows_back: bool = True) -> bool:
        """Deixa de seguir um usuário"""
        # Verifica whitelist
        if self.is_whitelisted(username):
            logger.info(f"🛡️  @{username} está na whitelist")
            return False
        
        if not self.rate_limiter.can_perform('unfollows', config.MAX_UNFOLLOWS_PER_HOUR):
            return False
        
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            HumanBehavior.random_delay(3, 5)
            
            # Verifica se segue de volta
            if check_follows_back:
                follows_back = self.check_if_follows_back(username)
                if follows_back:
                    logger.info(f"💚 @{username} segue de volta, mantendo")
                    if username in self.followed_users:
                        self.followed_users[username].follows_back = True
                        self.save_data()
                    return False
            
            # Clica em "Seguindo"
            following_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.SELECTORS['following_button']))
            )
            following_btn.click()
            HumanBehavior.random_delay(1, 2)
            
            # Confirma unfollow
            unfollow_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Deixar de seguir')]"))
            )
            unfollow_btn.click()
            
            # Atualiza registro
            if username in self.followed_users:
                self.followed_users[username].unfollowed_at = datetime.now().isoformat()
            
            self.rate_limiter.record_action('unfollows')
            self.daily_stats['unfollows_today'] += 1
            self.save_data()
            
            logger.info(f"✅ Deixou de seguir @{username}")
            HumanBehavior.random_delay(5, 10)
            return True
            
        except TimeoutException:
            logger.info(f"⏭️  Não está seguindo @{username}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao dar unfollow em @{username}: {e}")
            return False
    
    # ============================================
    # ESTRATÉGIAS
    # ============================================
    
    def follow_followers_of_target(self, target_username: str, 
                                    max_follows: int = 20,
                                    min_followers: int = 50,
                                    max_followers: int = 10000,
                                    skip_private: bool = True) -> int:
        """Segue seguidores de um perfil alvo"""
        logger.info(f"🎯 Seguindo seguidores de @{target_username}")
        
        followers = self.get_followers_list(target_username, max_follows * 2)
        followed_count = 0
        
        for username in followers:
            if followed_count >= max_follows:
                break
            
            # Pula se já processou
            if username in self.followed_users:
                continue
            
            # Verifica critérios do perfil
            try:
                self.driver.get(f"https://www.instagram.com/{username}/")
                HumanBehavior.random_delay(2, 4)
                
                # Pula privados
                if skip_private:
                    try:
                        self.driver.find_element(By.XPATH, "//span[contains(text(), 'Esta conta é privada')]")
                        continue
                    except:
                        pass
                
                # Verifica contagem de seguidores
                try:
                    followers_elem = self.driver.find_element(
                        By.XPATH, "//a[contains(@href, '/followers')]/span/span"
                    )
                    followers_text = followers_elem.text.replace('.', '').replace('k', '000').replace('m', '000000')
                    user_followers = int(followers_text)
                    
                    if not (min_followers <= user_followers <= max_followers):
                        continue
                except:
                    pass
                
                # Tenta seguir
                if self.follow_user(username, source=f"follower_of_{target_username}"):
                    followed_count += 1
                    
            except Exception as e:
                continue
        
        logger.info(f"✅ Seguiu {followed_count} usuários de @{target_username}")
        return followed_count
    
    def clean_non_followers(self, max_unfollows: int = 50, 
                           days_before_unfollow: int = 2) -> int:
        """Limpa quem não segue de volta"""
        logger.info("🧹 Iniciando limpeza de não-seguidores...")
        
        following = self.get_following_list()
        unfollowed_count = 0
        
        cutoff_date = datetime.now() - timedelta(days=days_before_unfollow)
        
        for username in following:
            if unfollowed_count >= max_unfollows:
                break
            
            # Verifica whitelist
            if self.is_whitelisted(username):
                continue
            
            # Verifica data de follow
            if username in self.followed_users:
                user = self.followed_users[username]
                if user.followed_at:
                    followed_date = datetime.fromisoformat(user.followed_at)
                    if followed_date > cutoff_date:
                        continue
            
            # Dá unfollow
            if self.unfollow_user(username, check_follows_back=True):
                unfollowed_count += 1
        
        logger.info(f"✅ Limpeza concluída: {unfollowed_count} unfollows")
        return unfollowed_count
    
    # ============================================
    # ESTATÍSTICAS
    # ============================================
    
    def get_stats(self) -> dict:
        """Retorna estatísticas completas"""
        total = len(self.followed_users)
        active = sum(1 for u in self.followed_users.values() if not u.unfollowed_at)
        unfollowed = total - active
        
        # Calcula follow-back rate
        checked = [u for u in self.followed_users.values() if u.follows_back is not None]
        follow_backs = sum(1 for u in checked if u.follows_back)
        follow_back_rate = (follow_backs / len(checked) * 100) if checked else 0
        
        # Por fonte
        sources = defaultdict(int)
        for u in self.followed_users.values():
            sources[u.source] += 1
        
        return {
            "total_historico": total,
            "seguindo_ativamente": active,
            "unfollows_realizados": unfollowed,
            "whitelist": len(self.whitelist),
            "taxa_follow_back": f"{follow_back_rate:.1f}%",
            "por_fonte": dict(sources),
            "hoje": dict(self.daily_stats)
        }

# Importações no final para evitar circular
from utils import load_json, save_json
