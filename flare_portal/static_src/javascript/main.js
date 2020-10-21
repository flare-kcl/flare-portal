import '@babel/polyfill';
import React from 'react';
import ReactDOM from 'react-dom';
import TestReact from './components/TestReact';
import MobileMenu from './components/mobile-menu';
import MobileSubMenu from './components/mobile-sub-menu';






// Add polyfill fix for forEach carousel
import foreachPolyfill from './polyfills/foreach-polyfill';

import '../sass/main.scss';

foreachPolyfill();

// Open the mobile menu callback
function openMobileMenu() {
    document.querySelector('body').classList.add('no-scroll');
    document.querySelector('[data-mobile-menu]').classList.add('is-visible');
}

// Close the mobile menu callback.
function closeMobileMenu() {
    document.querySelector('body').classList.remove('no-scroll');
    document.querySelector('[data-mobile-menu]').classList.remove('is-visible');
}

document.addEventListener('DOMContentLoaded', () => {
    /* eslint-disable no-restricted-syntax, no-new */
    

    

    

    for (const mobilemenu of document.querySelectorAll(MobileMenu.selector())) {
        new MobileMenu(mobilemenu, openMobileMenu, closeMobileMenu);
    }

    for (const mobilesubmenu of document.querySelectorAll(
        MobileSubMenu.selector(),
    )) {
        new MobileSubMenu(mobilesubmenu);
    }

    // Toggle subnav visibility
    for (const subnavBack of document.querySelectorAll('[data-subnav-back]')) {
        subnavBack.addEventListener('click', () => {
            subnavBack.parentNode.classList.remove('is-visible');
        });
    }

    

    

    // Test react - add a div with a data attribute of `data-test-react` to test
    for (const element of document.querySelectorAll('[data-test-react]')) {
        ReactDOM.render(<TestReact greeting="boo!" />, element);
    }
});
