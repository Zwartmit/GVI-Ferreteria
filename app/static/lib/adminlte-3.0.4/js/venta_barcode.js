// Código para el escáner de códigos de barras
document.addEventListener('DOMContentLoaded', function() {
    // Asegurarse de que estamos en la página correcta
    if (!document.getElementById('product-sale-rows')) return;

    // Elementos principales
    const productSaleRows = document.getElementById('product-sale-rows');
    const subtotalElement = document.getElementById('subtotal_sale');
    const dineroRecibidoInput = document.getElementById('money_received_sale');
    const cambioElement = document.getElementById('change_sale');
    let validationTimeout = null;

    // Variable para almacenar la última lectura del código de barras
    let lastBarcodeScan = '';
    let barcodeScanTimer = null;
    const BARCODE_SCAN_TIMEOUT = 100; // Tiempo en ms para determinar si es una entrada manual o escáner

    // Función para actualizar el color del stock según la cantidad
    function updateStockColor(stockElement, stockQuantity) {
        if (stockQuantity === 0) {
            stockElement.style.backgroundColor = 'red';
            stockElement.style.color = 'white';
        } else if (stockQuantity > 0 && stockQuantity <= 10) {
            stockElement.style.backgroundColor = '#ffce33';
            stockElement.style.color = 'white';
        } else if (stockQuantity > 10) {
            stockElement.style.backgroundColor = '#2b88c9';
            stockElement.style.color = 'white';
        } else {
            stockElement.style.backgroundColor = 'transparent';
            stockElement.style.color = 'black';
        }
    }

    // Función para procesar el código de barras escaneado
    function processBarcodeScan(barcode) {
        // Buscar si ya existe una fila con el producto (usando select2 correctamente)
        let filaExistente = null;
        document.querySelectorAll('#product-sale-rows tr').forEach(row => {
            const select = row.querySelector('.product-select');
            const selectVal = select ? $(select).val() : null;
            if (selectVal && selectVal == barcode) {
                filaExistente = row;
            }
        });
        if (filaExistente) {
            // Sumar cantidad y actualizar subtotal (no crear fila nueva)
            const inputCantidad = filaExistente.querySelector('.product-quantity');
            let cantidad = parseInt(inputCantidad.value) || 0;
            cantidad += 1;
            inputCantidad.value = cantidad;
            // Recalcula subtotal
            const precio = parseFloat(filaExistente.querySelector('.product-price').value) || 0;
            filaExistente.querySelector('.product-total').textContent = '$' + (cantidad * precio).toFixed(2);
            validateInputs(); // Actualizar totales
            return; // Termina aquí, nunca agrega fila nueva
        }

        // Solo si no existe, busca fila vacía o crea nueva
        console.log("Procesando código de barras:", barcode);
        
        $.ajax({
            url: '/app/venta/productos_api/',
            data: { term: barcode },
            dataType: 'json',
            success: function(data) {
                if (data.length === 0) {
                    // Producto no encontrado
                    Swal.fire({
                        title: 'Error!',
                        text: 'Código de barras no encontrado en el sistema.',
                        icon: 'error',
                    });
                    return;
                }
                
                const producto = data[0];
                console.log("Producto encontrado:", producto);
                
                // Antes de agregar, buscar si ya existe una fila con este producto
                let filaExistente = null;
                document.querySelectorAll('#product-sale-rows tr').forEach(row => {
                    const select = row.querySelector('.product-select');
                    const selectVal = select ? $(select).val() : null;
                    if (selectVal && selectVal == producto.id) {
                        filaExistente = row;
                    }
                });
                if (filaExistente) {
                    // Sumar cantidad y actualizar subtotal
                    const inputCantidad = filaExistente.querySelector('.product-quantity');
                    let cantidad = parseInt(inputCantidad.value) || 0;
                    cantidad += 1;
                    inputCantidad.value = cantidad;
                    const precio = parseFloat(filaExistente.querySelector('.product-price').value) || 0;
                    filaExistente.querySelector('.product-total').textContent = '$' + (cantidad * precio).toFixed(2);
                    validateInputs();
                    return;
                }
                // Si no existe, buscar una fila vacía
                let emptyRow = null;
                document.querySelectorAll('#product-sale-rows tr').forEach(row => {
                    const select = row.querySelector('.product-select');
                    if (select) {
                        const selectData = $(select).select2('data');
                        if (!selectData || selectData.length === 0 || !selectData[0].id) {
                            emptyRow = row;
                            console.log("Fila vacía encontrada");
                            return false; // Detener el bucle
                        }
                    }
                });
                
                // Si no hay filas vacías, crear una nueva
                if (!emptyRow) {
                    console.log("No hay filas vacías, creando una nueva");
                    addProductSaleRow();
                    emptyRow = document.querySelector('#product-sale-rows tr:last-child');
                }
                
                // Seleccionar el producto en la fila
                const select = $(emptyRow.querySelector('.product-select'));
                
                // Crear la opción y seleccionarla
                console.log("Añadiendo producto a fila vacía");
                const option = new Option(
                    `${producto.producto} - ${producto.id_presentacion__presentacion}`, 
                    producto.id, 
                    true, 
                    true
                );
                
                // Agregar datos adicionales a la opción
                option.valor = producto.valor;
                option.precio_venta = producto.precio_venta;
                option.cantidad = producto.cantidad;
                
                // Limpiar el select antes de agregar la nueva opción
                select.empty();
                select.append(option).trigger('change');
                // Asegurar que el valor del input sea el id correcto
                select.val(producto.id).trigger('change');
                select[0].value = producto.id;
                
                // Unificar el estilo de la selección para que se vea igual que los productos seleccionados manualmente
                const selectContainer = $(select).data('select2').$container;
                if (selectContainer) {
                    // Asegurarse de que el contenedor tiene el mismo estilo que los seleccionados manualmente
                    selectContainer.find('.select2-selection').addClass('select2-selection--manual');
                }
                
                // Establecer los valores en la fila
                const priceInput = emptyRow.querySelector('.product-price');
                const stockSpan = emptyRow.querySelector('.product-stock');
                const quantityInput = emptyRow.querySelector('.product-quantity');
                
                // Siempre usar el precio_venta si está disponible, sino usar valor como respaldo
                priceInput.value = producto.precio_venta !== undefined && producto.precio_venta !== null ? 
                    producto.precio_venta : producto.valor;
                stockSpan.textContent = producto.cantidad || 0;
                quantityInput.max = producto.cantidad || 0;
                quantityInput.value = 1; // Establecer cantidad a 1 por defecto
                
                // Actualizar visualización
                updateStockColor(stockSpan, producto.cantidad);
                validateInputs(); // Actualizar totales
            },
            error: function(xhr, status, error) {
                console.error("Error al buscar producto:", error);
                Swal.fire({
                    title: 'Error!',
                    text: 'Error al buscar el producto: ' + error,
                    icon: 'error',
                });
            }
        });
    }

    // Validar inputs y calcular totales
    function validateInputs() {
        // Validación de productos repetidos
        let productos = [];
        let productoRepetido = false;
        document.querySelectorAll('#product-sale-rows tr').forEach(row => {
            const select = $(row.querySelector('.product-select')).val();
            if (select) {
                if (productos.includes(select)) {
                    productoRepetido = true;
                } else {
                    productos.push(select);
                }
            }
        });
        if (productoRepetido) {
            Swal.fire({
                title: 'Advertencia',
                text: 'Este producto ya está seleccionado',
                icon: 'warning',
            });
            document.getElementById('btn-guardar-venta').disabled = true;
        } else {
            document.getElementById('btn-guardar-venta').disabled = false;
        }

        let isValid = true;
        let subtotal = 0;

        document.querySelectorAll('#product-sale-rows tr').forEach(row => {
            const select = $(row.querySelector('.product-select')).val();
            const quantityInput = row.querySelector('.product-quantity');
            const priceInput = row.querySelector('.product-price');
            const stockSpan = row.querySelector('.product-stock');

            // Solo validar si hay un producto seleccionado
            if (select) {
                const quantity = Number(quantityInput.value);
                const price = Number(priceInput.value);
                const maxQuantity = Number(quantityInput.max);

                if (quantity <= 0 || quantity > maxQuantity) {
                    quantityInput.classList.add('error');
                    isValid = false;
                } else {
                    quantityInput.classList.remove('error');
                }

                if (price < 0) {
                    priceInput.classList.add('error');
                    isValid = false;
                } else {
                    priceInput.classList.remove('error');
                }

                const total = (quantity * price).toFixed(2);
                row.querySelector('.product-total').textContent = `$${total}`;

                subtotal += parseFloat(total);
            }
        });

        subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        return isValid;
    }

    // Calcular cambio
    function calculateChange() {
        const dineroRecibido = parseFloat(dineroRecibidoInput.value) || 0;
        const subtotal = parseFloat(subtotalElement.textContent.replace('$', '')) || 0;
        const cambio = dineroRecibido - subtotal;

        cambioElement.value = cambio.toFixed(2);
    }

    // Agregar una fila de producto para venta
    function addProductSaleRow() {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="product-sale-column">
                <input class="product-id product-select" style="width: 100%;" required />
            </td>
            <td class="quantity-sale-column"><input type="number" class="product-quantity" min="1" required></td>
            <td class="price-sale-column"><input type="number" class="product-price" min="0" step="0.01" required readonly></td>
            <td class="stock-sale-column"><span class="product-stock">0</span></td>
            <td class="delete-sale-column">
                <i type="button" class="delete-row fas fa-trash-alt" style="color: #9b0707; font-size: 25px;"
                    onmouseover="this.style.color='#ff0000';"
                    onmouseout="this.style.color='#9b0707';"></i>
            </td>
            <td><span class="product-total">$0.00</span></td>
        `;

        $(row.querySelector('.product-select')).select2({
            placeholder: 'Seleccione un producto',
            ajax: {
                url: '/app/venta/productos_api/', 
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(producto => ({
                            id: producto.id,
                            text: `${producto.producto} - ${producto.id_presentacion__presentacion}`,
                            valor: producto.valor,
                            precio_venta: producto.precio_venta, // Agregar precio_venta
                            cantidad: producto.cantidad,
                            producto_nombre: producto.producto  // Guardar el nombre exacto del producto
                        }))
                    };
                },
                cache: true
            }
        }).on('select2:select', function (e) {
            const data = e.params.data;
            const priceInput = row.querySelector('.product-price');
            const stockSpan = row.querySelector('.product-stock');
            const quantityInput = row.querySelector('.product-quantity');
            
            // Guardar los datos completos del producto en el elemento select para accederlos después
            $(this).data('producto_data', data);
            
            // Siempre usar el precio_venta si está disponible, sino usar valor como respaldo
            priceInput.value = data.precio_venta !== undefined && data.precio_venta !== null ? 
                data.precio_venta : data.valor;
            stockSpan.textContent = data.cantidad || 0;
            quantityInput.max = data.cantidad || 0;
            quantityInput.value = 1; // Establecer cantidad a 1 por defecto

            // Aplicar el mismo estilo tanto para productos escaneados como seleccionados manualmente
            const selectContainer = $(this).data('select2').$container;
            if (selectContainer) {
                // Actualizar el texto visible
                selectContainer.find('.select2-selection__placeholder').text(data.text);
                
                // Asegurar que todos los productos tengan el mismo estilo visual
                selectContainer.find('.select2-selection').css({
                    'background-color': '#fff',
                    'color': '#333',
                    'font-weight': 'normal'
                });
            }
            
            updateStockColor(stockSpan, data.cantidad);
            validateInputs();

            // --- AGREGAR OTRA FILA AUTOMÁTICAMENTE SI TODAS LAS FILAS TIENEN PRODUCTO ---
            // Si todas las filas tienen producto seleccionado, agregar una nueva fila
            const filas = document.querySelectorAll('#product-sale-rows tr');
            let hayFilaVacia = false;
            filas.forEach(fila => {
                const select = $(fila).find('.product-select');
                if (!select.val()) {
                    hayFilaVacia = true;
                }
            });
            if (!hayFilaVacia) {
                setTimeout(() => {
                    const nuevaFila = addProductSaleRow();
                    // Abrir el select2 de la nueva fila para facilitar el escaneo/manual
                    const nuevoSelect = nuevaFila.querySelector('.product-select');
                    if (nuevoSelect) {
                        $(nuevoSelect).select2('open');
                    }
                }, 200);
            }
        });

        productSaleRows.appendChild(row);

        row.querySelector('.product-quantity').addEventListener('input', function() {
            clearTimeout(validationTimeout);
            validationTimeout = setTimeout(validateInputs, 500);
        });
        
        row.querySelector('.product-price').addEventListener('input', validateInputs);
        
        row.querySelector('.delete-row').addEventListener('click', function () {
            const rows = document.querySelectorAll('#product-sale-rows tr');

            if (rows.length === 1) {
                Swal.fire({
                    title: 'Advertencia!',
                    text: 'No puedes eliminar la última fila.',
                    icon: 'warning',
                });
                return;
            }

            Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    row.remove();
                    validateInputs();
                    Swal.fire(
                        'Eliminado!',
                        'La fila ha sido eliminada.',
                        'success'
                    );
                }
            });
        });

        validateInputs();
        return row;
    }

    // Agregamos un listener para capturar la entrada del escáner de código de barras
    document.addEventListener('keydown', function(e) {
        // Solo procesar si estamos en la página de ventas
        if (!document.getElementById('product-sale-rows')) return;
        
        // Detectar si es una entrada rápida (típica de escáneres)
        if (e.key !== 'Enter') {
            clearTimeout(barcodeScanTimer);
            lastBarcodeScan += e.key;
            
            barcodeScanTimer = setTimeout(() => {
                lastBarcodeScan = ''; // Limpiar si la entrada es muy lenta (probablemente manual)
            }, BARCODE_SCAN_TIMEOUT);
        } else if (lastBarcodeScan) {
            // Si presiona Enter y hay una lectura acumulada, procesar el código de barras
            processBarcodeScan(lastBarcodeScan);
            lastBarcodeScan = '';
            e.preventDefault(); // Prevenir comportamiento por defecto del Enter
        }
    });

    // Si el dinero recibido cambia, calcular el cambio
    if (dineroRecibidoInput) {
        dineroRecibidoInput.addEventListener('input', calculateChange);
    }

    // Exponer la función para que pueda ser llamada desde el HTML
    window.addProductSaleRow = addProductSaleRow;
    window.processBarcodeScan = processBarcodeScan;
    window.clearProductRows = function() {
        // Eliminar todas las filas
        while (productSaleRows.firstChild) {
            productSaleRows.removeChild(productSaleRows.firstChild);
        }
        // Agregar una nueva fila vacía y abrir el select2
        const row = addProductSaleRow();
        setTimeout(() => {
            const select = row.querySelector('.product-select');
            if (select) {
                $(select).select2('open');
            }
        }, 200);
        // Limpiar los campos de dinero recibido y cambio
        if (dineroRecibidoInput) {
            dineroRecibidoInput.value = '';
        }
        if (cambioElement) {
            cambioElement.value = '';
        }
        validateInputs();
    }
    
    // Agregar la primera fila si no hay ninguna
    if (productSaleRows && productSaleRows.children.length === 0) {
        const row = addProductSaleRow();
        // Esperar a que select2 esté inicializado y luego abrirlo
        setTimeout(() => {
            const select = row.querySelector('.product-select');
            if (select) {
                $(select).select2('open');
            }
        }, 200);
    }
});
