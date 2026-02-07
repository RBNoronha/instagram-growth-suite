"""
Bot Principal - Núcleo do Sistema
Integra todos os módulos
"""
import os
import pickle
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    NoSuchElementException, 
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException
)

from utils import (
    HumanBehavior, RateLimiter, logger, 
    safe_execute, print_banner, print_success, 
    print_error, print_info, print_warning
)
from config import config

class InstagramBot:
    """Bot principal de automação Instagram"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.rate_limiter = RateLimiter()
        self.is_logged_in = False
        
        # Módulos (lazy loading)
        self._followers_manager = None
        self._growth_engine = None
        self._content_scheduler = None
        self._analytics_engine = None
    
    # ============================================
    # PROPRIEDADES DOS MÓDULOS
    # ============================================
    
    @property
    def followers_manager(self):
        if self._followers_manager is None:
            from followers_manager import FollowersManager
            self._followers_manager = FollowersManager(self.driver, self.wait, self.rate_limiter)
        return self._followers_manager
    
    @property
    def growth_engine(self):
        if self._growth_engine is None:
            from growth_engine import GrowthEngine
            self._growth_engine = GrowthEngine(
                self.driver, self.wait, self.rate_limiter, self.followers_manager
            )
        return self._growth_engine
    
    @property
    def content_scheduler(self):
        if self._content_scheduler is None:
            from content_scheduler import ContentScheduler
            self._content_scheduler = ContentScheduler(self.driver, self.wait)
        return self._content_scheduler
    
    @property
    def analytics_engine(self):
        if self._analytics_engine is None:
            from analytics_engine import AnalyticsEngine
            self._analytics_engine = AnalyticsEngine(self.driver, self.wait)
        return self._analytics_engine
    
    # ============================================
    # SETUP DO NAVEGADOR
    # ============================================
    
    def setup_driver(self):
        """Configura o Chrome com anti-detecção"""
        print_info("Configurando navegador...")
        
        chrome_options = Options()
        
        if config.HEADLESS:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
        
        # Anti-detecção
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        if config.CUSTOM_USER_AGENT:
            chrome_options.add_argument(f"user-agent={config.CUSTOM_USER_AGENT}")
        else:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Proxy
        if config.PROXY_URL:
            chrome_options.add_argument(f"--proxy-server={config.PROXY_URL}")
        
        # Perfil persistente
        profile_dir = os.path.join(config.DATA_DIR, "chrome_profile")
        os.makedirs(profile_dir, exist_ok=True)
        chrome_options.add_argument(f"user-data-dir={profile_dir}")
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Remove flag de webdriver
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            self.wait = WebDriverWait(self.driver, config.BROWSER_TIMEOUT)
            
            print_success("Navegador configurado!")
            
        except WebDriverException as e:
            print_error(f"Erro ao configurar navegador: {e}")
            raise
    
    # ============================================
    # LOGIN
    # ============================================
    
    @safe_execute(max_retries=3)
    def login(self, force_new: bool = False) -> bool:
        """Realiza login no Instagram"""
        
        if not config.IG_USERNAME or not config.IG_PASSWORD:
            print_error("Credenciais não configuradas!")
            print_info("Configure IG_USERNAME e IG_PASSWORD no arquivo .env")
            return False
        
        if not self.driver:
            self.setup_driver()
        
        print_info("Acessando Instagram...")
        self.driver.get("https://www.instagram.com/")
        HumanBehavior.random_delay(3, 5)
        
        # Tenta cookies primeiro
        if not force_new:
            if self._try_cookie_login():
                return True
        
        # Login manual
        print_info("Realizando login...")
        
        try:
            # Preenche usuário
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS['username_input']))
            )
            
            for char in config.IG_USERNAME:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            HumanBehavior.random_delay(0.5, 1.5)
            
            # Preenche senha
            password_input = self.driver.find_element(
                By.CSS_SELECTOR, config.SELECTORS['password_input']
            )
            
            for char in config.IG_PASSWORD:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            HumanBehavior.random_delay(1, 2)
            
            # Clica em login
            login_btn = self.driver.find_element(
                By.CSS_SELECTOR, config.SELECTORS['login_button']
            )
            login_btn.click()
            
            HumanBehavior.random_delay(5, 8)
            
            # Lida com modais
            self._dismiss_modals()
            
            # Verifica login
            if self._check_login_status():
                self._save_cookies()
                self.is_logged_in = True
                print_success("Login realizado com sucesso!")
                return True
            else:
                print_error("Não foi possível confirmar login")
                return False
                
        except Exception as e:
            print_error(f"Erro no login: {e}")
            return False
    
    def _try_cookie_login(self) -> bool:
        """Tenta login via cookies"""
        try:
            if os.path.exists(config.COOKIES_FILE):
                with open(config.COOKIES_FILE, 'rb') as f:
                    cookies = pickle.load(f)
                
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                self.driver.refresh()
                HumanBehavior.random_delay(3, 5)
                
                if self._check_login_status():
                    self.is_logged_in = True
                    print_success("Login restaurado via cookies!")
                    return True
        except Exception as e:
            logger.warning(f"Não foi possível restaurar cookies: {e}")
        
        return False
    
    def _save_cookies(self):
        """Salva cookies da sessão"""
        try:
            cookies = self.driver.get_cookies()
            with open(config.COOKIES_FILE, 'wb') as f:
                pickle.dump(cookies, f)
            logger.info("Cookies salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar cookies: {e}")
    
    def _dismiss_modals(self):
        """Fecha modais pós-login"""
        modals = [
            config.SELECTORS['not_now_button'],
            config.SELECTORS['save_info_button'],
            "//button[contains(text(), 'Not Now')]",
            "//button[contains(text(), 'Agora não')]"
        ]
        
        for modal in modals:
            try:
                btn = self.driver.find_element(By.XPATH, modal)
                btn.click()
                HumanBehavior.random_delay(1, 2)
            except:
                pass
    
    def _check_login_status(self) -> bool:
        """Verifica se está logado"""
        try:
            self.driver.find_element(By.XPATH, "//a[contains(@href, '/direct/inbox')]")
            return True
        except:
            return False
    
    # ============================================
    # AÇÕES BÁSICAS
    # ============================================
    
    def like_post(self, post_url: str) -> bool:
        """Curti um post"""
        if not self.rate_limiter.can_perform('likes', config.MAX_LIKES_PER_HOUR):
            return False
        
        try:
            self.driver.get(post_url)
            HumanBehavior.random_delay(2, 4)
            
            like_btn = self.driver.find_element(
                By.CSS_SELECTOR, config.SELECTORS['like_button']
            )
            like_btn.click()
            
            self.rate_limiter.record_action('likes')
            logger.info(f"❤️  Post curtido: {post_url[:50]}...")
            return True
            
        except:
            logger.info("Post já curtido ou erro")
            return False
    
    # ============================================
    # MÉTODOS DE ALTO NÍVEL
    # ============================================
    
    def run_growth_session(self, session_type: str = "balanced"):
        """Executa sessão de crescimento completa"""
        if not self.is_logged_in:
            if not self.login():
                return
        
        self.growth_engine.run_growth_session(session_type)
    
    def schedule_week_content(self, content_folder: str = None):
        """Agenda conteúdo para a semana"""
        if not self.is_logged_in:
            self.login()
        
        # Usa analytics para horários ótimos
        optimal = self.analytics_engine.export_best_times()
        hours = [optimal["primeiro_post"], optimal["segundo_post"]]
        
        self.content_scheduler.auto_schedule_week(
            content_folder=content_folder,
            posts_per_day=config.POSTS_PER_DAY,
            optimal_hours=hours
        )
    
    def analyze_and_report(self):
        """Analisa e gera relatório"""
        if not self.is_logged_in:
            self.login()
        
        print(self.analytics_engine.generate_report())
    
    def get_stats(self) -> dict:
        """Retorna estatísticas completas"""
        stats = {
            "rate_limiter": self.rate_limiter.get_stats(),
        }
        
        if self._followers_manager:
            stats["followers"] = self.followers_manager.get_stats()
        
        if self._growth_engine:
            stats["growth_weekly"] = self.growth_engine.get_weekly_report()
        
        return stats
    
    # ============================================
    # UTILITÁRIOS
    # ============================================
    
    def screenshot(self, filename: str = None):
        """Tira screenshot"""
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = os.path.join(config.LOGS_DIR, filename)
        self.driver.save_screenshot(filepath)
        print_info(f"Screenshot salvo: {filepath}")
    
    def quit(self):
        """Encerra o bot"""
        if self.driver:
            self.driver.quit()
            print_info("Navegador encerrado")

# Importações adicionais
import time
from datetime import datetime
