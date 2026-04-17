"""
Дымовое тестирование веб-сервиса Sauce Demo
https://www.saucedemo.com/
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import make_screenshot


BASE_URL = "https://www.saucedemo.com/"
PASSWORD = "secret_sauce"

# Локаторы
USERNAME_INPUT = (By.ID, "user-name")
PASSWORD_INPUT = (By.ID, "password")
LOGIN_BUTTON = (By.ID, "login-button")
ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message-container")
INVENTORY_ITEM = (By.CLASS_NAME, "inventory_item")
ADD_TO_CART_BUTTON = (By.CLASS_NAME, "btn_primary")
CART_BUTTON = (By.CLASS_NAME, "shopping_cart_link")
CHECKOUT_BUTTON = (By.ID, "checkout")
FIRST_NAME_INPUT = (By.ID, "first-name")
LAST_NAME_INPUT = (By.ID, "last-name")
POSTAL_CODE_INPUT = (By.ID, "postal-code")
CONTINUE_BUTTON = (By.ID, "continue")
FINISH_BUTTON = (By.ID, "finish")
COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
MENU_BUTTON = (By.ID, "react-burger-menu-btn")
SIDEBAR = (By.ID, "sidebar-container")


class TestSauceDemo:
    """Класс с тестами для Sauce Demo"""

    def test_login_standard_user(self, driver, screenshot_dir):
        """Тест 1: Успешный вход стандартного пользователя"""
        driver.get(BASE_URL)
        
        # Заполнение полей ввода
        driver.find_element(*USERNAME_INPUT).send_keys("standard_user")
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        
        # Нажатие на кнопку входа
        driver.find_element(*LOGIN_BUTTON).click()
        
        # Проверка успешного входа
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inventory_item"))
        )
        
        # Скролл страницы по локатору (первый товар)
        item = driver.find_element(*INVENTORY_ITEM)
        driver.execute_script("arguments[0].scrollIntoView();", item)
        
        # Скриншот
        make_screenshot(driver, "01_login_success", screenshot_dir)
        
        assert driver.current_url == f"{BASE_URL}inventory.html"

    def test_add_to_cart(self, driver, screenshot_dir):
        """Тест 2: Добавление товара в корзину"""
        # Вход
        driver.get(BASE_URL)
        driver.find_element(*USERNAME_INPUT).send_keys("standard_user")
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        driver.find_element(*LOGIN_BUTTON).click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inventory_item"))
        )
        
        # Добавление первого товара в корзину
        add_button = driver.find_element(*ADD_TO_CART_BUTTON)
        driver.execute_script("arguments[0].scrollIntoView();", add_button)
        add_button.click()
        
        # Скриншот после добавления в корзину
        make_screenshot(driver, "02_add_to_cart", screenshot_dir)
        
        # Проверка, что товар добавлен (появился бейдж на корзине)
        cart_badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
        assert cart_badge.is_displayed()
        assert cart_badge.text == "1"

    def test_checkout_process(self, driver, screenshot_dir):
        """Тест 3: Оформление заказа"""
        # Вход и добавление товара
        driver.get(BASE_URL)
        driver.find_element(*USERNAME_INPUT).send_keys("standard_user")
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        driver.find_element(*LOGIN_BUTTON).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inventory_item"))
        )

        driver.find_element(*ADD_TO_CART_BUTTON).click()
        driver.find_element(*CART_BUTTON).click()

        # Переход к оформлению
        driver.find_element(*CHECKOUT_BUTTON).click()

        # Заполнение данных доставки
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "first-name"))
        )
        driver.find_element(*FIRST_NAME_INPUT).send_keys("John")
        driver.find_element(*LAST_NAME_INPUT).send_keys("Doe")
        driver.find_element(*POSTAL_CODE_INPUT).send_keys("12345")

        # Скролл к кнопке Continue
        continue_button = driver.find_element(*CONTINUE_BUTTON)
        driver.execute_script("arguments[0].scrollIntoView();", continue_button)

        # Скриншот перед продолжением
        make_screenshot(driver, "03_checkout_info", screenshot_dir)

        # Продолжение оформления - переход к странице доставки
        continue_button.click()

        # Ожидание загрузки страницы с методами доставки (Overview)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "summary_info"))
        )

        # Скролл к кнопке Finish
        finish_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "finish"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", finish_button)
        finish_button.click()

        # Проверка успешного завершения
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "complete-header"))
        )

        # Финальный скриншот
        make_screenshot(driver, "04_order_complete", screenshot_dir)

        complete_header = driver.find_element(*COMPLETE_HEADER)
        assert "Thank you for your order" in complete_header.text

    def test_locked_out_user(self, driver, screenshot_dir):
        """Тест 4: Попытка входа заблокированного пользователя"""
        driver.get(BASE_URL)
        
        # Заполнение полей данными заблокированного пользователя
        driver.find_element(*USERNAME_INPUT).send_keys("locked_out_user")
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        driver.find_element(*LOGIN_BUTTON).click()
        
        # Проверка появления сообщения об ошибке
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message-container"))
        )
        
        # Скриншот ошибки
        make_screenshot(driver, "05_locked_out_error", screenshot_dir)
        
        error_message = driver.find_element(*ERROR_MESSAGE)
        assert "Sorry, this user has been locked out" in error_message.text

    def test_performance_glitch_user(self, driver, screenshot_dir):
        """Тест 5: Вход пользователя с задержкой производительности"""
        driver.get(BASE_URL)
        
        # Заполнение полей
        driver.find_element(*USERNAME_INPUT).send_keys("performance_glitch_user")
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        driver.find_element(*LOGIN_BUTTON).click()
        
        # Ожидание загрузки страницы (может быть задержка)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inventory_item"))
        )
        
        # Скролл страницы
        sidebar = driver.find_element(By.ID, "react-burger-menu-btn")
        driver.execute_script("arguments[0].scrollIntoView();", sidebar)
        
        # Скриншот
        make_screenshot(driver, "06_performance_user", screenshot_dir)
        
        assert driver.current_url == f"{BASE_URL}inventory.html"

    def test_menu_scroll(self, driver, screenshot_dir):
        """Тест 6: Открытие меню и скролл по странице"""
        # Вход
        driver.get(BASE_URL)
        driver.find_element(*USERNAME_INPUT).send_keys("standard_user")
        driver.find_element(*PASSWORD_INPUT).send_keys(PASSWORD)
        driver.find_element(*LOGIN_BUTTON).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "react-burger-menu-btn"))
        )

        # Скролл к кнопке меню
        menu_button = driver.find_element(*MENU_BUTTON)
        driver.execute_script("arguments[0].scrollIntoView();", menu_button)

        # Открытие меню
        menu_button.click()

        # Ожидание появления элементов меню
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "inventory_sidebar_link"))
        )

        # Скриншот с открытым меню
        make_screenshot(driver, "07_menu_open", screenshot_dir)

        # Проверка, что меню открыто (ссылка All Items видима)
        all_items_link = driver.find_element(By.ID, "inventory_sidebar_link")
        assert all_items_link.is_displayed()
        assert "All Items" in all_items_link.text
