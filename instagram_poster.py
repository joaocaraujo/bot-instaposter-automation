from playwright.sync_api import sync_playwright
import logging
import os
import time
from pathlib import Path
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_poster.log'),
        logging.StreamHandler()
    ]
)

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class InstagramPoster:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = None
        self.page = None
        self.setup_browser()

    def setup_browser(self):
        try:
            user_data_dir = f'C:\\Users\\{os.getenv("USERNAME")}\\AppData\\Local\\Google\\Chrome\\User Data'
            profile_directory = 'Default'
            
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                viewport={'width': 1366, 'height': 768},
                channel='chrome',
                args=[
                    f'--profile-directory={profile_directory}',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-notifications',
                    '--window-size=1366,768',
                    '--window-position=0,0'
                ],
                ignore_default_args=['--enable-automation']
            )
            self.page = self.browser.new_page()
            
            self.page.evaluate("""
                window.resizeTo(1366, 768);
                window.moveTo(0, 0);
            """)
            
            logging.info("Browser iniciado com perfil do usuário")
        except Exception as e:
            logging.error(f"Erro ao configurar browser: {e}")
            raise

    def login(self):
        try:
            self.page.goto('https://www.instagram.com/red_agenciamkt/')
            print("Aguardando carregamento do perfil...")
            
            login_button = self.page.locator('text=Entrar').first
            if login_button.is_visible():
                print("❌ ERRO: Usuário não está logado no Instagram!")
                print("Por favor, faça login manualmente no Chrome e tente novamente.")
                return False
            
            self.page.wait_for_selector('[aria-label="Nova publicação"]', timeout=20000)
            print("✓ Login confirmado - Perfil carregado com sucesso!")
            return True
        except Exception as e:
            print("❌ ERRO: Não foi possível confirmar o login.")
            logging.error(f"Erro no login: {e}")
            return False

    @retry(max_attempts=3, delay=1)
    def create_new_post(self):
        try:
            # Verificar URL atual antes de tentar criar novo post
            if "instagram.com/create" in self.page.url:
                self.page.goto("https://www.instagram.com/")
                time.sleep(1)
            
            logging.info("Iniciando criação de nova postagem")
            
            try:
                close_button = self.page.locator('button[aria-label="Fechar"]').first
                if close_button.is_visible():
                    close_button.click()
                    time.sleep(1)
            except:
                try:
                    self.page.keyboard.press('Escape')
                    time.sleep(1)
                except:
                    pass
            
            selectors = [
                '[aria-label="Nova publicação"]',
                'text=Criar',
                '[role="button"]:has-text("Criar")'
            ]
            
            for selector in selectors:
                try:
                    self.page.click(selector)
                    break
                except:
                    continue
            
            self.page.click('text=Postar')
            return True
        except Exception as e:
            logging.error(f"Erro ao criar nova postagem: {e}")
            return False

    @retry(max_attempts=3, delay=1)
    def select_image(self, image_path):
        try:
            logging.info(f"Selecionando imagem: {image_path}")
            
            image_path = os.path.abspath(image_path)
            
            self.page.wait_for_selector('text=Selecionar do computador', timeout=5000)
            self.page.click('text=Selecionar do computador')
            
            time.sleep(1)  # Reduzido de 2 para 1
            
            import pyautogui
            pyautogui.write(image_path)
            time.sleep(0.5)  # Reduzido de 1 para 0.5
            pyautogui.press('enter')
            logging.info("Arquivo selecionado via pyautogui")
            
            try:
                self.page.wait_for_selector('[aria-label="Selecionar corte"]', timeout=10000)  # Reduzido de 15000
                logging.info("Imagem carregada com sucesso")
                
                time.sleep(2)  # Reduzido de 3
                
                if not self.configure_image_format():
                    raise Exception("Falha ao configurar formato 4:5")
                
                return True
                
            except Exception as e:
                logging.error(f"Erro após upload da imagem: {e}")
                return False
            
        except Exception as e:
            logging.error(f"Erro ao selecionar imagem: {e}")
            self.handle_discard_dialog()
            return False

    def configure_image_format(self):
        try:
            time.sleep(2)
            
            crop_selectors = [
                '[aria-label="Selecionar corte"]',
                'svg[aria-label="Selecionar corte"]',
                '//div[.//svg[@aria-label="Selecionar corte"]]',
                '//div[contains(@class, "x9f619")]//svg[@aria-label="Selecionar corte"]'
            ]
            
            for selector in crop_selectors:
                try:
                    if selector.startswith('//'):
                        crop_button = self.page.locator(f'xpath={selector}').first
                    else:
                        crop_button = self.page.locator(selector).first
                    
                    if crop_button and crop_button.is_visible():
                        crop_button.click()
                        logging.info("Botão de corte encontrado e clicado")
                        break
                except Exception as e:
                    logging.warning(f"Falha ao usar selector {selector}: {e}")
                    continue
            
            time.sleep(2)
            
            ratio_selectors = [
                '[aria-label="Proporção 4:5"]',
                'text=4:5',
                '//button[contains(text(), "4:5")]',
                '//div[contains(text(), "4:5")]'
            ]
            
            for selector in ratio_selectors:
                try:
                    if selector.startswith('//'):
                        ratio_button = self.page.locator(f'xpath={selector}').first
                    else:
                        ratio_button = self.page.locator(selector).first
                    
                    if ratio_button and ratio_button.is_visible():
                        ratio_button.click()
                        logging.info("Formato 4:5 selecionado")
                        break
                except Exception as e:
                    logging.warning(f"Falha ao selecionar 4:5 com selector {selector}: {e}")
                    continue
            
            time.sleep(1)
            
            for i in range(2):
                try:
                    next_button = self.page.locator('text=Avançar').first
                    if next_button and next_button.is_visible():
                        next_button.click()
                        logging.info(f"Clique em Avançar {i+1}/2")
                        time.sleep(1)
                except Exception as e:
                    logging.error(f"Erro ao clicar em Avançar: {e}")
                    return False
            
            return True
        except Exception as e:
            logging.error(f"Erro ao configurar formato: {e}")
            return False

    def handle_discard_dialog(self):
        """Trata o diálogo de descartar post"""
        try:
            cancel_button = self.page.locator('button:has-text("Cancelar")')
            if cancel_button.is_visible():
                cancel_button.click()
                logging.info("Diálogo de 'Descartar post' fechado")
        except Exception as e:
            logging.warning(f"Erro ao tratar diálogo de descarte: {e}")

    @retry(max_attempts=3, delay=1)
    def add_description_and_tag(self, base_text):
        try:
            logging.info("Iniciando processo")
            
            username = extract_username(base_text)
            
            print("Adicionando descrição...")
            try:
                # Localiza e clica no campo de legenda
                caption_field = self.page.locator('[aria-label="Escreva uma legenda..."]').first
                caption_field.click()
                time.sleep(0.2)
                
                # Limpa o campo
                self.page.keyboard.press('Control+A')
                self.page.keyboard.press('Delete')
                time.sleep(0.2)
                
                # Digita o texto em chunks maiores para maior velocidade
                for chunk in [base_text[i:i+200] for i in range(0, len(base_text), 200)]:
                    caption_field.type(chunk, delay=5)  # Delay muito baixo para maior velocidade
                    time.sleep(0.05)  # Pequena pausa entre chunks
                
                print("✓ Descrição adicionada com sucesso")
            except Exception as desc_error:
                print(f"❌ Erro ao adicionar descrição: {str(desc_error)}")
                raise
            
            if username:
                try:
                    print(f"Tentando marcar usuário: {username}")
                    
                    modal = self.page.locator('div[role="dialog"]').first
                    if modal:
                        box = modal.bounding_box()
                        if box:
                            click_x = box['x'] + (box['width'] * 0.3)
                            click_y = box['y'] + (box['height'] * 0.3)
                            self.page.mouse.click(click_x, click_y)
                            time.sleep(1)  # Reduzido de 2
                    
                    search_input = self.page.locator('input[placeholder="Pesquisar"]').first
                    if search_input.is_visible():  # Otimizado
                        search_input.click()
                        search_input.fill("")
                        username_clean = username.replace('@', '')
                        search_input.fill(username_clean)
                        print(f"Pesquisando por: {username_clean}")
                        time.sleep(1)  # Reduzido de 2
                        
                        time.sleep(1)  # Reduzido de 2
                        
                        selectors = [
                            'button._acmy._acm-',
                            'div._acmr',
                            f'div._acmu:has-text("{username_clean}")',
                            f'button:has(div._acmu:has-text("{username_clean}"))'
                        ]
                        
                        for selector in selectors:
                            try:
                                result = self.page.locator(selector).first
                                if result.is_visible():  # Otimizado
                                    print(f"Encontrou resultado usando selector: {selector}")
                                    result.click(timeout=5000)
                                    time.sleep(0.5)  # Reduzido de 1
                                    
                                    if self.page.locator('button:has-text("Concluir")').is_visible():  # Otimizado
                                        self.page.locator('button:has-text("Concluir")').click()
                                        print("✓ Usuário marcado com sucesso")
                                        return True
                                    break
                            except Exception as click_error:
                                print(f"Tentativa de clique falhou: {click_error}")
                                continue
                
                except Exception as mark_error:
                    print(f"⚠️ Erro ao marcar usuário: {str(mark_error)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no processo: {str(e)}")
            return False

    @retry(max_attempts=3, delay=1)
    def share_post(self):
        try:
            # Clica no botão Compartilhar
            self.page.click('text=Compartilhar')
            print("✓ Botão compartilhar clicado")
            
            # Aguarda a confirmação de compartilhamento
            self.page.wait_for_selector('text=Seu post foi compartilhado', timeout=10000)  # Reduzido de 15000
            print("✓ Post compartilhado com sucesso")
            
            # Tenta fechar a tela de confirmação
            try:
                # Tenta clicar no botão Fechar
                close_button = self.page.locator('button[aria-label="Fechar"]').first
                if close_button.is_visible():
                    close_button.click()
                else:
                    # Fallback para Escape
                    self.page.keyboard.press('Escape')
                print("✓ Tela de confirmação fechada")
            except:
                # Fallback para Escape se tudo falhar
                self.page.keyboard.press('Escape')
            
            time.sleep(1)  # Reduzido de 2
            return True
            
        except Exception as e:
            print(f"❌ Erro ao compartilhar: {str(e)}")
            return False

    def close(self):
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logging.info("Browser fechado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao fechar browser: {e}")

    def handle_stuck_upload(self):
        """Tenta recuperar de um upload travado"""
        try:
            try:
                self.page.keyboard.press('Escape')
                time.sleep(1)
            except:
                pass
            
            try:
                cancel_button = self.page.locator('button:has-text("Cancelar")').first
                if cancel_button and cancel_button.is_visible():
                    cancel_button.click()
            except:
                pass
            
            time.sleep(1)
            
            return True
        except Exception as e:
            logging.error(f"Erro ao tentar recuperar upload travado: {e}")
            return False

    def ensure_no_windows_dialog(self):
        """Garante que não há janelas de diálogo do Windows abertas"""
        try:
            import pyautogui
            for _ in range(2):
                pyautogui.press('esc')
                time.sleep(0.5)
            return True
        except Exception as e:
            logging.error(f"Erro ao tentar fechar diálogos: {e}")
            return False

    def mark_user_alternative(self, username):
        try:
            self.page.mouse.move(400, 300)
            self.page.mouse.click(400, 300)
            time.sleep(1)
            
            search_input = self.page.locator('input[name="userSearchInput"]')
            if search_input.is_visible():
                search_input.fill(username.replace('@', ''))
                time.sleep(1)
                
                self.page.keyboard.press('ArrowDown')
                time.sleep(0.5)
                self.page.keyboard.press('Enter')
                time.sleep(1)
                
                self.page.keyboard.press('Enter')
                
                return True
        except Exception as e:
            logging.error(f"Erro no método alternativo de marcação: {e}")
            return False

    def click_tag_area(self):
        try:
            image = self.page.locator('img[alt="Foto"]').first
            if image:
                box = image.bounding_box()
                if box:
                    self.page.mouse.click(
                        box['x'] + box['width']/2,
                        box['y'] + box['height']/4
                    )
                    return True
        except Exception as e:
            logging.error(f"Erro ao clicar na área de marcação: {e}")
            return False

def read_base_texts(file_path):
    """Lê os textos base do arquivo e remove apenas o texto usado"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Divide os textos mantendo o delimitador
        texts = content.split('#atendimentopersonalizado')
        texts = [text.strip() for text in texts if text.strip()]
        
        if texts:
            # Pega o primeiro texto e adiciona o delimitador
            current_text = texts[0] + '#atendimentopersonalizado'
            
            # Remove apenas o primeiro texto, mantendo os demais
            remaining_texts = '#atendimentopersonalizado'.join(texts[1:])
            
            # Salva os textos restantes
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(remaining_texts)
            
            logging.info(f"Texto usado removido do arquivo. Restam {len(texts)-1} textos.")
            return [current_text]
            
        logging.info("Nenhum texto encontrado no arquivo")
        return []
            
    except Exception as e:
        logging.error(f"Erro ao ler textos base: {e}")
        return []

def extract_username(text):
    """Extrai o nome de usuário do Instagram do texto"""
    import re
    match = re.search(r'@(\w+\.?\w*)', text)
    return match.group(1) if match else None

def main():
    images_folder = r"G:\Redguias\postsdodia"
    base_texts_file = os.path.join(images_folder, "textobase.txt")
    gpt_texts_file = os.path.join(images_folder, "zgpttextos.txt")  # Novo arquivo para limpar
    
    for path in [images_folder, base_texts_file]:
        if not os.path.exists(path):
            print(f"Erro: O caminho {path} não existe!")
            return

    poster = InstagramPoster()
    
    try:
        if not poster.login():
            return

        images = sorted(
            [f for f in os.listdir(images_folder) if f.endswith('.png')],
            key=lambda x: int(x.split('.')[0])
        )
        
        if not images:
            print("Erro: Nenhuma imagem PNG encontrada na pasta!")
            return
            
        print(f"\nEncontradas {len(images)} imagens para postar")
        print("Ordem de postagem:", ", ".join(images))
        
        successful_posts = []
        
        for i, image in enumerate(images):
            print(f"\n{'='*50}")
            print(f"Processando imagem {i+1} de {len(images)}: {image}")
            print(f"{'='*50}\n")
            
            # Lê o próximo texto disponível
            base_texts = read_base_texts(base_texts_file)
            if not base_texts:
                print("Não há mais textos disponíveis para postagem")
                break
                
            current_base_text = base_texts[0]
            
            for attempt in range(3):
                if attempt > 0:
                    print(f"Tentativa {attempt + 1} de 3")
                
                if not all([
                    poster.create_new_post(),
                    poster.select_image(os.path.join(images_folder, image))
                ]):
                    continue
                
                if not poster.add_description_and_tag(current_base_text):
                    continue
                
                if poster.share_post():
                    print(f"Postagem {i+1} concluída com sucesso!")
                    successful_posts.append(image)
                    
                    # Apaga a imagem logo após o post ser concluído
                    try:
                        os.remove(os.path.join(images_folder, image))
                        print(f"✓ Imagem {image} removida com sucesso")
                    except Exception as e:
                        print(f"⚠️ Erro ao remover imagem {image}: {str(e)}")
                    
                    time.sleep(5)
                    break
            else:
                print(f"Não foi possível postar a imagem {image}")
        
        print(f"\nProcesso finalizado! {len(successful_posts)} imagens postadas e removidas.")
        
        # Limpa o arquivo zgpttextos.txt após todas as postagens
        try:
            with open(gpt_texts_file, 'w', encoding='utf-8') as file:
                file.write('')  # Escreve string vazia para limpar o arquivo
            print("✓ Arquivo zgpttextos.txt limpo com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao limpar arquivo zgpttextos.txt: {str(e)}")
                
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
    finally:
        poster.close()

if __name__ == "__main__":
    main() 