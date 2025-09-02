document.addEventListener('DOMContentLoaded', function() {

    const menuToggle = document.getElementById('menuToggle');
    const mobileSidebar = document.getElementById('mobileSidebar');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    
    // Toggle para mostrar el menú móvil
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            mobileSidebar.classList.add('show');
            sidebarBackdrop.classList.add('show');
            document.body.classList.add('sidebar-open');
        });
    }
    
    // Función para cerrar el menú móvil
    function closeMobileMenu() {
        mobileSidebar.classList.remove('show');
        sidebarBackdrop.classList.remove('show');
        document.body.classList.remove('sidebar-open');
    }
    
    // Cerrar menú al hacer clic en el botón de cierre
    if (closeSidebar) {
        closeSidebar.addEventListener('click', closeMobileMenu);
    }
    
    // Cerrar menú al hacer clic en el backdrop
    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeMobileMenu);
    }
    
    // Cerrar menú al hacer clic en un enlace en pantallas pequeñas
    const mobileNavLinks = document.querySelectorAll('#mobileSidebar a');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    // Detectar cambios de tamaño de pantalla
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768 && document.body.classList.contains('sidebar-open')) {
            closeMobileMenu();
        }
    });
});
