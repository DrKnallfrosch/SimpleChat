import unittest
import os
import tempfile
import sqlite3
import time
import logging
from authentication.userbase_db import UserManager

# Test-spezifischer Logger
test_logger = logging.getLogger('TestUserManager')


class TestUserManager(unittest.TestCase):

    def setUp(self):
        """Setup für jeden Test - mit besserer DB-Verwaltung"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Warte bis die Datei wirklich verfügbar ist
        time.sleep(0.1)

        self.user_manager = UserManager(db_name=self.db_path)
        test_logger.info(f"Test Setup: Temporäre DB {os.path.basename(self.db_path)}")

    def tearDown(self):
        """Cleanup nach jedem Test - mit besseren Löschmechanismen"""
        # Warte kurz bevor Löschung versucht wird
        time.sleep(0.1)

        # Versuche die Datei zu löschen, ignoriere Fehler falls sie noch gesperrt ist
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if os.path.exists(self.db_path):
                    os.unlink(self.db_path)
                    break
            except PermissionError:
                if attempt < max_attempts - 1:
                    time.sleep(0.2)  # Warte 200ms zwischen Versuchen
                else:
                    test_logger.warning(
                        f"Konnte DB {os.path.basename(self.db_path)} nicht löschen - wird vom System bereinigt")

        test_logger.info(f"Test Cleanup: DB {os.path.basename(self.db_path)} bereinigt")

    def test_01_database_initialization(self):
        """Test-ID: TM-001 - Datenbank-Initialisierung"""
        test_logger.info("Test TM-001: Datenbank-Initialisierung")

        # Prüfe ob Tabelle existiert
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()

        self.assertIsNotNone(result, "Tabelle 'users' sollte existieren")
        self.assertEqual(result[0], 'users', "Tabellenname sollte 'users' sein")
        test_logger.info("✅ TM-001: Datenbank-Initialisierung erfolgreich")

    def test_02_create_user_success(self):
        """Test-ID: TM-002 - Erfolgreiche Benutzererstellung"""
        test_logger.info("Test TM-002: Erfolgreiche Benutzererstellung")

        result = self.user_manager.create_user("testuser", "password123")

        self.assertTrue(result, "Benutzererstellung sollte True zurückgeben")
        self.assertTrue(self.user_manager.check_user_exists("testuser"),
                        "Benutzer sollte in Datenbank existieren")
        test_logger.info("✅ TM-002: Benutzererstellung erfolgreich")

    def test_03_create_user_duplicate(self):
        """Test-ID: TM-003 - Doppelte Benutzererstellung"""
        test_logger.info("Test TM-003: Doppelte Benutzererstellung")

        # Ersten Benutzer erstellen
        result1 = self.user_manager.create_user("testuser", "password123")
        self.assertTrue(result1, "Erste Benutzererstellung sollte erfolgreich sein")

        # Zweiten Benutzer mit gleichem Namen
        result2 = self.user_manager.create_user("testuser", "different_password")
        self.assertFalse(result2, "Zweite Benutzererstellung sollte False zurückgeben")
        test_logger.info("✅ TM-003: Doppelte Benutzererstellung korrekt verhindert")

    def test_04_authenticate_success(self):
        """Test-ID: TM-004 - Erfolgreiche Authentifizierung"""
        test_logger.info("Test TM-004: Erfolgreiche Authentifizierung")

        self.user_manager.create_user("testuser", "password123")
        result = self.user_manager.authenticate("testuser", "password123")

        self.assertTrue(result, "Authentifizierung mit korrektem Passwort sollte True sein")
        test_logger.info("✅ TM-004: Authentifizierung erfolgreich")

    def test_05_authenticate_wrong_password(self):
        """Test-ID: TM-005 - Authentifizierung mit falschem Passwort"""
        test_logger.info("Test TM-005: Authentifizierung mit falschem Passwort")

        self.user_manager.create_user("testuser", "password123")
        result = self.user_manager.authenticate("testuser", "wrong_password")

        self.assertFalse(result, "Authentifizierung mit falschem Passwort sollte False sein")
        test_logger.info("✅ TM-005: Falsche Authentifizierung korrekt erkannt")

    def test_06_authenticate_nonexistent_user(self):
        """Test-ID: TM-006 - Authentifizierung nicht existenter Benutzer"""
        test_logger.info("Test TM-006: Authentifizierung nicht existenter Benutzer")

        result = self.user_manager.authenticate("nonexistent", "password123")

        self.assertFalse(result, "Authentifizierung nicht existenter Benutzer sollte False sein")
        test_logger.info("✅ TM-006: Nicht existenter Benutzer korrekt erkannt")

    def test_07_delete_user_success(self):
        """Test-ID: TM-007 - Erfolgreiches Benutzerlöschen"""
        test_logger.info("Test TM-007: Erfolgreiches Benutzerlöschen")

        self.user_manager.create_user("testuser", "password123")
        self.assertTrue(self.user_manager.check_user_exists("testuser"))

        result = self.user_manager.delete_user("testuser")
        self.assertTrue(result, "Löschen sollte True zurückgeben")
        self.assertFalse(self.user_manager.check_user_exists("testuser"),
                         "Benutzer sollte nicht mehr existieren")
        test_logger.info("✅ TM-007: Benutzerlöschen erfolgreich")

    def test_08_delete_user_nonexistent(self):
        """Test-ID: TM-008 - Löschen nicht existenter Benutzer"""
        test_logger.info("Test TM-008: Löschen nicht existenter Benutzer")

        result = self.user_manager.delete_user("nonexistent")

        self.assertFalse(result, "Löschen nicht existenter Benutzer sollte False sein")
        test_logger.info("✅ TM-008: Löschen nicht existenter Benutzer korrekt")

    def test_09_change_password_success(self):
        """Test-ID: TM-009 - Erfolgreiche Passwortänderung"""
        test_logger.info("Test TM-009: Erfolgreiche Passwortänderung")

        self.user_manager.create_user("testuser", "old_password")

        # Passwort ändern
        result = self.user_manager.change_user_password("testuser", "new_password")
        self.assertTrue(result, "Passwortänderung sollte True zurückgeben")

        # Mit neuem Passwort authentifizieren
        self.assertTrue(self.user_manager.authenticate("testuser", "new_password"),
                        "Authentifizierung mit neuem Passwort sollte funktionieren")
        self.assertFalse(self.user_manager.authenticate("testuser", "old_password"),
                         "Authentifizierung mit altem Passwort sollte nicht funktionieren")
        test_logger.info("✅ TM-009: Passwortänderung erfolgreich")

    def test_10_change_password_nonexistent(self):
        """Test-ID: TM-010 - Passwortänderung nicht existenter Benutzer"""
        test_logger.info("Test TM-010: Passwortänderung nicht existenter Benutzer")

        result = self.user_manager.change_user_password("nonexistent", "new_password")

        self.assertFalse(result, "Passwortänderung nicht existenter Benutzer sollte False sein")
        test_logger.info("✅ TM-010: Passwortänderung nicht existenter Benutzer korrekt")

    def test_11_special_characters(self):
        """Test-ID: TM-011 - Sonderzeichen in Benutzername und Passwort"""
        test_logger.info("Test TM-011: Sonderzeichen in Benutzername und Passwort")

        special_username = "user@name-123_测试"
        special_password = "p@ssw0rd!$%&*()_+测试"

        result = self.user_manager.create_user(special_username, special_password)
        self.assertTrue(result, "Benutzer mit Sonderzeichen sollte erstellt werden")

        auth_result = self.user_manager.authenticate(special_username, special_password)
        self.assertTrue(auth_result, "Authentifizierung mit Sonderzeichen sollte funktionieren")
        test_logger.info("✅ TM-011: Sonderzeichen korrekt verarbeitet")

    def test_12_sql_injection_prevention(self):
        """Test-ID: TM-012 - SQL-Injection Prävention"""
        test_logger.info("Test TM-012: SQL-Injection Prävention")

        injection_username = "test'; DROP TABLE users; --"
        result = self.user_manager.create_user(injection_username, "password")

        self.assertTrue(result, "SQL-Injection sollte als normaler Benutzername behandelt werden")
        self.assertTrue(self.user_manager.check_user_exists(injection_username),
                        "SQL-Injection Benutzername sollte existieren")
        test_logger.info("✅ TM-012: SQL-Injection Prävention erfolgreich")

    def test_13_concurrent_operations(self):
        """Test-ID: TM-013 - Aufeinanderfolgende Operationen"""
        test_logger.info("Test TM-013: Aufeinanderfolgende Operationen")

        # Erstellen
        self.user_manager.create_user("testuser", "password1")
        self.assertTrue(self.user_manager.authenticate("testuser", "password1"))

        # Passwort ändern
        self.user_manager.change_user_password("testuser", "password2")
        self.assertTrue(self.user_manager.authenticate("testuser", "password2"))
        self.assertFalse(self.user_manager.authenticate("testuser", "password1"))

        # Löschen
        self.user_manager.delete_user("testuser")
        self.assertFalse(self.user_manager.check_user_exists("testuser"))
        self.assertFalse(self.user_manager.authenticate("testuser", "password2"))
        test_logger.info("✅ TM-013: Aufeinanderfolgende Operationen erfolgreich")


if __name__ == '__main__':
    unittest.main(verbosity=2)