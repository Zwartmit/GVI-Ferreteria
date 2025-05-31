document.addEventListener("DOMContentLoaded", function() {
    const buttonLabels = {
        "Fuente legible": "Fuente Legible",
        "Baja saturación": "Baja Saturación",
        "Alta saturación": "Alta Saturación",
        "Alto contraste": "Alto Contraste",
        "Bajo contraste": "Bajo Contraste",
    };

    document.querySelectorAll('.asw-btn').forEach(button => {
        const key = button.querySelector('.material-icons').nextSibling.nodeValue.trim();
        if (buttonLabels[key]) {
            button.querySelector('.material-icons').nextSibling.nodeValue = buttonLabels[key];
        }
    });
});

