
/*
Ticki (Ticket System) App
GitHub: https://github.com/Mhadi-1382/ticki
*/

// ===== Navbar Mobile
function navbarMobileFunc() {
    var navbarMobileOverlay = document.getElementById('navbarMoblieOverlay');
    navbarMobileOverlay.classList.toggle('navbar-mobile-toggle');
}

// ===== Modal
function modalFunc(id) {
    var modalOverlayId = document.getElementById(id);
    modalOverlayId.classList.toggle('modal-toggle');
}

// ===== Tab
var tabTicketOpenId = document.getElementById('tabTicketOpen');
var tabTicketActiveOpen = document.getElementById('tabTicketActiveOpen');
var tabTicketCloseId = document.getElementById('tabTicketClose');
var tabTicketActiveClose = document.getElementById('tabTicketActiveClose');
function tabTicketOpenFunc() {
    tabTicketCloseId.style.display = 'none';
    tabTicketOpenId.style.display = 'block';
    tabTicketActiveClose.classList.remove('tab-active');
    tabTicketActiveOpen.classList.add('tab-active');
}
function tabTicketCloseFunc() {
    tabTicketOpenId.style.display = 'none';
    tabTicketCloseId.style.display = 'block';
    tabTicketActiveOpen.classList.remove('tab-active');
    tabTicketActiveClose.classList.add('tab-active');
}
