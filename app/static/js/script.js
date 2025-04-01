const productos = {
    "1001": { nombre: "Panela", precio: 2500 },
    "1002": { nombre: "Agua", precio: 1200 },
    "1003": { nombre: "Manzana", precio: 3000 },
    "1004": { nombre: "Arroz", precio: 2750 },
    "1005": { nombre: "Mermelada", precio: 4500 },
    "1006": { nombre: "Queso", precio: 5000 },
    "1007": { nombre: "Papel", precio: 1800 },
    "1008": { nombre: "Café", precio: 6000 },
    "1009": { nombre: "Leche", precio: 1500 },
    "1010": { nombre: "Huevos", precio: 2000 },
    "1011": { nombre: "Jugos", precio: 3250 },
    "1012": { nombre: "Jabón", precio: 1800 },
    "1013": { nombre: "Mortadela", precio: 3500 },
    "1014": { nombre: "Harina", precio: 2000 },
    "1015": { nombre: "Chocolate", precio: 4000 },
    
};  

function verificarPrecio() {
    const productoCodigo = document.getElementById('producto').value.trim();
    const resultado = document.getElementById('resultado');
    console.log("Código ingresado por el usuario:", productoCodigo);

    if (productoCodigo === "salir") {
        resultado.textContent = "Gracias por consultar.";
        limpiarResultadoConRetardo();
        return;
    }
    if (productos[productoCodigo]) {
        const productoEncontrado = productos[productoCodigo];
        resultado.textContent = `${productoEncontrado.nombre} - $${productoEncontrado.precio.toFixed(2)}`;
    } else {
        resultado.textContent = "Producto no encontrado.";
    }
    document.getElementById('producto').value = "";

    limpiarResultadoConRetardo();
}
function limpiarResultadoConRetardo() {
    setTimeout(() => {
        const resultado = document.getElementById('resultado');
        resultado.textContent = ""; 
    }, 4000); 
}

