/**
 * DARC Mitgliedsantrag – Floating CTA
 *
 * Blendet den mitlaufenden Button automatisch nach kurzer Verzögerung ein,
 * damit er auch auf großen Bildschirmen / kurzen Seiten ohne Scrollen sichtbar
 * ist. Wird vorher gescrollt, erscheint er sofort.
 *
 * Es werden KEINE personenbezogenen Daten und keine dauerhaften Marker
 * gespeichert – nur ein sessionStorage-Flag pro Element, das beim Schließen des
 * Tabs verfällt.
 */
(function () {
    'use strict';

    var REVEAL_DELAY = 800; // ms: spätestens nach dieser Zeit einblenden.
    var REVEAL_AFTER = 200; // px Scroll-Tiefe, ab der sofort eingeblendet wird.

    function storageKey(el) {
        return 'darcFloatingDismissed_' + (el.getAttribute('data-uid') || '0');
    }

    function isDismissed(el) {
        if (el.getAttribute('data-dismissible') !== '1') {
            return false;
        }
        try {
            return window.sessionStorage.getItem(storageKey(el)) === '1';
        } catch (e) {
            return false;
        }
    }

    function dismiss(el) {
        el.classList.remove('is-visible');
        window.setTimeout(function () { el.setAttribute('hidden', 'hidden'); }, 350);
        try {
            window.sessionStorage.setItem(storageKey(el), '1');
        } catch (e) { /* sessionStorage nicht verfügbar – egal */ }
    }

    function reveal(el) {
        el.removeAttribute('hidden');
        // Doppeltes rAF, damit der Display-Wechsel die Transition auslöst.
        window.requestAnimationFrame(function () {
            window.requestAnimationFrame(function () { el.classList.add('is-visible'); });
        });
    }

    function setup(el) {
        if (isDismissed(el)) {
            return;
        }

        var closeBtn = el.querySelector('.darc-floating__close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () { dismiss(el); });
        }

        var shown = false;
        var timer = null;

        function show() {
            if (shown) {
                return;
            }
            shown = true;
            window.removeEventListener('scroll', onScroll);
            if (timer) {
                window.clearTimeout(timer);
            }
            reveal(el);
        }

        function onScroll() {
            if ((window.pageYOffset || document.documentElement.scrollTop) > REVEAL_AFTER) {
                show();
            }
        }

        // Garantierte Einblendung nach kurzer Verzögerung (auch ohne Scrollen).
        timer = window.setTimeout(show, REVEAL_DELAY);
        // Früher einblenden, sobald der Besucher scrollt.
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    function init() {
        var elements = Array.prototype.slice.call(
            document.querySelectorAll('[data-darc-floating]')
        );
        elements.forEach(setup);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
