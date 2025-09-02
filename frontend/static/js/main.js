// Script principal para todas las páginas
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Formatear fechas ISO en elementos con la clase 'fecha-iso'
    formatearFechasISO();
    
    // Mensaje de bienvenida en la consola
    console.log('¡Bienvenido a Radical K9!');
});

/**
 * Función para formatear fechas ISO a formato amigable (hora Ecuador GMT-5)
 * Busca todos los elementos con la clase 'fecha-iso' y convierte su contenido
 */
function formatearFechasISO() {
    const elementosFecha = document.querySelectorAll('.fecha-iso');
    
    elementosFecha.forEach(function(elemento) {
        const fechaISO = elemento.textContent.trim();
        if (fechaISO) {
            try {
                const fechaObj = new Date(fechaISO);
                const dia = String(fechaObj.getDate()).padStart(2, '0');
                const mes = String(fechaObj.getMonth() + 1).padStart(2, '0'); 
                const anio = fechaObj.getFullYear();
                const hora = String(fechaObj.getHours()).padStart(2, '0');
                const minutos = String(fechaObj.getMinutes()).padStart(2, '0');
                
                const fechaFormateada = `${dia}/${mes}/${anio} ${hora}:${minutos}`;
                elemento.textContent = fechaFormateada;
            } catch (error) {
                console.error('Error al formatear fecha:', error);
            }
        }
    });
}
