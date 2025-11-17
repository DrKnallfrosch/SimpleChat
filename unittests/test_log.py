#!/usr/bin/env python3
"""
Test-Runner für SimpleChat Bottle DB
Protokolliert Ergebnisse in tests.log
"""

import unittest
import sys
import os
import datetime
import logging
from test_userbase_db import TestUserManager


def setup_logging():
    """Setup für Logging in tests.log"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tests.log', mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('SimpleChatTests')


def run_user_manager_tests(logger):
    """Führt UserManager Tests durch"""
    logger.info("=" * 60)
    logger.info("START: UserManager Unittests")
    logger.info("=" * 60)

    # Test-Suite erstellen und ausführen
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUserManager)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # Ergebnisse protokollieren
    logger.info("UserManager Test-Zusammenfassung:")
    logger.info(f"  Tests durchgeführt: {result.testsRun}")
    logger.info(f"  Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"  Fehlgeschlagen: {len(result.failures)}")
    logger.info(f"  Fehler: {len(result.errors)}")

    if result.failures:
        logger.info("Fehlgeschlagene Tests:")
        for test, traceback in result.failures:
            logger.info(f"  - {test}: {traceback.splitlines()[-1]}")

    if result.errors:
        logger.info("Fehlerhafte Tests:")
        for test, traceback in result.errors:
            logger.info(f"  - {test}: {traceback.splitlines()[-1]}")

    return result.wasSuccessful()


def manual_integration_tests(logger):
    """Führt manuelle Integrationstests durch"""
    logger.info("=" * 60)
    logger.info("START: Manuelle Integrationstests")
    logger.info("=" * 60)

    tests = [
        {
            "name": "Datenbank-Initialisierung",
            "steps": ["UserManager Instanz erstellen", "Tabelle prüfen"],
            "expected": "Tabelle 'users' sollte existieren",
            "result": "❓ Noch nicht durchgeführt"
        },
        {
            "name": "Benutzer-Registrierung",
            "steps": ["Neuen Benutzer erstellen", "In Datenbank überprüfen"],
            "expected": "Benutzer sollte in Datenbank gespeichert sein",
            "result": "❓ Noch nicht durchgeführt"
        },
        {
            "name": "Login-Funktionalität",
            "steps": ["Mit korrekten Credentials anmelden", "Mit falschen Credentials anmelden"],
            "expected": "Erfolg bei korrekten, Fehler bei falschen Daten",
            "result": "❓ Noch nicht durchgeführt"
        },
        {
            "name": "Passwort-Änderung",
            "steps": ["Passwort ändern", "Mit neuem Passwort anmelden"],
            "expected": "Login mit neuem Passwort sollte funktionieren",
            "result": "❓ Noch nicht durchgeführt"
        },
        {
            "name": "Account-Löschung",
            "steps": ["Account löschen", "Existenz prüfen"],
            "expected": "Benutzer sollte nicht mehr existieren",
            "result": "❓ Noch nicht durchgeführt"
        }
    ]

    for test in tests:
        logger.info(f"Test: {test['name']}")
        logger.info(f"  Schritte: {', '.join(test['steps'])}")
        logger.info(f"  Erwartet: {test['expected']}")
        logger.info(f"  Ergebnis: {test['result']}")
        logger.info("")

    return True


def performance_tests(logger):
    """Führt Performance-Tests durch"""
    logger.info("=" * 60)
    logger.info("START: Performance-Tests")
    logger.info("=" * 60)

    try:
        from authentication.userbase_db import UserManager
        import time

        # Temporäre Datenbank für Performance-Tests
        test_db = "performance_test.db"
        if os.path.exists(test_db):
            os.remove(test_db)

        user_manager = UserManager(db_name=test_db)

        # Massen-Benutzer erstellen
        start_time = time.time()
        for i in range(100):
            user_manager.create_user(f"perfuser{i}", f"password{i}")
        create_time = time.time() - start_time

        # Massen-Authentifizierung
        start_time = time.time()
        for i in range(100):
            user_manager.authenticate(f"perfuser{i}", f"password{i}")
        auth_time = time.time() - start_time

        logger.info(f"Performance-Ergebnisse:")
        logger.info(f"  100 Benutzer erstellen: {create_time:.2f}s")
        logger.info(f"  100 Authentifizierungen: {auth_time:.2f}s")
        logger.info(f"  Durchschnitt pro Operation: {(create_time + auth_time) / 200 * 1000:.2f}ms")

        # Aufräumen
        if os.path.exists(test_db):
            os.remove(test_db)

    except Exception as e:
        logger.error(f"Performance-Test fehlgeschlagen: {e}")
        return False

    return True


def main():
    """Hauptfunktion für Test-Durchführung"""
    logger = setup_logging()

    logger.info("🚀 SimpleChat Bottle DB - Testprotokoll")
    logger.info(f"📅 Gestartet: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    # 1. Unittests
    unit_success = run_user_manager_tests(logger)
    logger.info("")

    # 2. Performance-Tests
    perf_success = performance_tests(logger)
    logger.info("")

    # 3. Manuelle Tests (Template)
    manual_integration_tests(logger)
    logger.info("")

    # Gesamtergebnis
    logger.info("=" * 60)
    logger.info("ENDE: Test-Zusammenfassung")
    logger.info("=" * 60)

    if unit_success and perf_success:
        logger.info("🎉 ALLE TESTS ERFOLGREICH")
        exit_code = 0
    else:
        logger.error("💥 EINIGE TESTS FEHLGESCHLAGEN")
        exit_code = 1

    logger.info(f"📅 Beendet: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())