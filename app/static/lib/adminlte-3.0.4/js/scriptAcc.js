// VENTA DE CUENTA //
document.addEventListener('DOMContentLoaded', function () {
    
    const productRows = document.getElementById('product-rows');
    const dishRows = document.getElementById('dish-rows');
    const subtotalElement = document.getElementById('subtotal');
    const dineroRecibidoInput = document.getElementById('dinero_recibido');
    const cambioElement = document.getElementById('cambio');
    let validationTimeout = null;

    let productRowCounter = 1;
    let dishRowCounter = 1;

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

    function addProductRow() {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="product-column" id="product-column-${productRowCounter}">
                <input id="product-id-${productRowCounter}" class="product-id product-select" style="width: 100%;" required />
            </td>
            <td class="quantity-column" id="quantity-column-${productRowCounter}">
                <input id="product-quantity-${productRowCounter}" type="number" class="product-quantity" min="1" required>
            </td>
            <td class="price-column" id="price-column-${productRowCounter}">
                <input id="product-price-${productRowCounter}" type="number" class="product-price" min="0" step="0.01" required readonly>
            </td>
            <td class="stock-column" id="stock-column-${productRowCounter}">
                <span id="product-stock-${productRowCounter}" class="product-stock">0</span>
            </td>
            <td class="delete-column">
                <i type="button" id="delete-row-${productRowCounter}" class="delete-row fas fa-trash-alt" style="color: #04644B; font-size: 25px;"
                    onmouseover="this.style.color='#ff0000';"
                    onmouseout="this.style.color='#04644B';"></i>
            </td>
            <td><span id="product-total-${productRowCounter}" class="product-total">$0.00</span></td>
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
                            text:`${producto.producto} - ${producto.id_presentacion__presentacion} (${producto.id_presentacion__unidad_medida})`,
                            valor: producto.valor,
                            cantidad: producto.cantidad
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
            
            priceInput.value = data.valor || 0;
            stockSpan.textContent = data.cantidad || 0;
            quantityInput.max = data.cantidad || 0;
            quantityInput.value = 1; 

            updateStockColor(stockSpan, data.cantidad);

            $(this).data('select2').$container.find('.select2-selection__placeholder').text(data.text);

            validateInputs();
        });

        productRows.appendChild(row);

        row.querySelector('.product-quantity').addEventListener('input', function() {
            clearTimeout(validationTimeout);
            validationTimeout = setTimeout(validateInputs, 500);
        });
        row.querySelector('.product-price').addEventListener('input', validateInputs);
        
        row.querySelector('.delete-row').addEventListener('click', function () {
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

        productRowCounter++;
        validateInputs();
    }

    function addDishRow() {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="dish-column" id="dish-column-${dishRowCounter}">
                <input id="dish-id-${dishRowCounter}" class="dish-id dish-select" style="width: 100%;" required />
            </td>
            <td class="quantity-dish-column" id="quantity-dish-column-${dishRowCounter}">
                <input id="dish-quantity-${dishRowCounter}" type="number" class="dish-quantity" min="1" required>
            </td>
            <td class="price-dish-column" id="price-dish-column-${dishRowCounter}">
                <input id="dish-price-${dishRowCounter}" type="number" class="dish-price" min="0" step="0.01" required readonly>
            </td>
            <td class="delete-dish-column">
                <i type="button" id="delete-dish-row-${dishRowCounter}" class="delete-dish-row fas fa-trash-alt" style="color: #04644B; font-size: 25px;"
                    onmouseover="this.style.color='#ff0000';"
                    onmouseout="this.style.color='#04644B';"></i>
            </td>
            <td><span id="dish-total-${dishRowCounter}" class="dish-total">$0.00</span></td>
        `;
    
        $(row.querySelector('.dish-select')).select2({
            placeholder: 'Seleccione un plato',
            ajax: {
                url: '/app/venta/platos_api/', 
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return { term: params.term };
                },
                processResults: function (data) {
                    return {
                        results: data.map(plato => ({
                            id: plato.id,
                            text: plato.plato,
                            valor: plato.valor,
                        }))
                    };
                },
                cache: true
            }
        }).on('select2:select', function (e) {
            const data = e.params.data;
            const priceInput = row.querySelector('.dish-price');
            const quantityInput = row.querySelector('.dish-quantity');
            
            priceInput.value = data.valor || 0;
            quantityInput.value = 1; 
    
            $(this).data('select2').$container.find('.select2-selection__placeholder').text(data.text);
    
            validateInputs();
        });
        
        dishRows.appendChild(row);
    
        row.querySelector('.dish-quantity').addEventListener('input', function() {
            clearTimeout(validationTimeout);
            validationTimeout = setTimeout(validateInputs, 500);
        });
        row.querySelector('.dish-price').addEventListener('input', validateInputs);

        row.querySelector('.delete-dish-row').addEventListener('click', function () {
          
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
    
        dishRowCounter++;
        validateInputs();
    }

    function validateInputs() {
        let isValid = true;
        let productIds = new Set();
        let dishIds = new Set(); 
        let subtotal = 0;
        let duplicateError = false;
    
        const productRows = document.querySelectorAll('#product-rows tr');
        const dishRows = document.querySelectorAll('#dish-rows tr');
    
        // Validación de filas vacías
        if (productRows.length === 0 && dishRows.length === 0) {
            Swal.fire({
                title: 'Error!',
                text: 'No se puede guardar la venta sin al menos un producto o plato.',
                icon: 'error',
            });
            isValid = false;
        }
    
        // Calcular subtotal de los productos
        productRows.forEach(row => {
            const select = $(row.querySelector('.product-select')).val();
            const quantityInput = row.querySelector('.product-quantity');
            const priceInput = row.querySelector('.product-price');
            const stockSpan = row.querySelector('.product-stock');
    
            const quantity = Number(quantityInput.value);
            const price = Number(priceInput.value);
            const maxQuantity = Number(quantityInput.max);
    
            if (productIds.has(select)) {
                $(row.querySelector('.product-select')).next().addClass('error');
                isValid = false;
                duplicateError = true;
            } else {
                $(row.querySelector('.product-select')).next().removeClass('error');
                productIds.add(select);
            }
    
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
        });
    
        // Calcular subtotal de los platos
        dishRows.forEach(row => {
            const select = $(row.querySelector('.dish-select')).val();
            const quantityInput = row.querySelector('.dish-quantity');
            const priceInput = row.querySelector('.dish-price');
    
            const quantity = Number(quantityInput.value);
            const price = Number(priceInput.value);
    
            if (dishIds.has(select)) {
                $(row.querySelector('.dish-select')).next().addClass('error');
                isValid = false;
                duplicateError = true;
            } else {
                $(row.querySelector('.dish-select')).next().removeClass('error');
                dishIds.add(select);
            }
    
            if (price < 0) {
                priceInput.classList.add('error');
                isValid = false;
            } else {
                priceInput.classList.remove('error');
            }
    
            const total = (quantity * price).toFixed(2);
            row.querySelector('.dish-total').textContent = `$${total}`;
    
            subtotal += parseFloat(total);
        });
    
        subtotal = subtotal.toFixed(2);
        subtotalElement.textContent = `$${subtotal}`;
    
        if (duplicateError) {
            Swal.fire({
                title: 'Error!',
                text: 'No se pueden guardar productos o platillos duplicados.',
                icon: 'error',
            });
            isValid = false;
        }
    
        return isValid && !duplicateError;
    }
    
    
    function calculateChange() {
        const dineroRecibido = parseFloat(dineroRecibidoInput.value) || 0;
        const subtotal = parseFloat(subtotalElement.textContent.replace('$', '')) || 0;
        const cambio = dineroRecibido - subtotal;
    
        cambioElement.value = cambio.toFixed(2);
    }

    $('.client-select').select2({
        placeholder: 'Buscar cliente',
        ajax: {
            url: '/app/venta/clientes_api/',
            dataType: 'json',
            delay: 250,

            data: function (params) {
                return { term: params.term };
            },
            processResults: function (data) {
                return {
                    results: data.map(cliente => ({
                        id: cliente.id,
                        text: `${cliente.tipo_documento}: ${cliente.numero_documento} - ${cliente.nombre}`,
                        nombre: cliente.nombre,
                        tipo_documento: cliente.tipo_documento,
                        numero_documento: cliente.numero_documento,
                        email: cliente.email,
                        pais_telefono: cliente.pais_telefono,
                        telefono: cliente.telefono
                    }))
                };
            },
            cache: true
        }
    }).on('select2:select', function (e) {
        const data = e.params.data;
        console.log('Cliente seleccionado:', data);
        document.getElementById('client-name').value = data.nombre;
        document.getElementById('client-document_type').value = data.tipo_documento;
        document.getElementById('client-document_number').value = data.numero_documento;
        document.getElementById('client-email').value = data.email;
        document.getElementById('client-phone_prefix').value = data.pais_telefono;
        document.getElementById('client-phone_number').value = data.telefono;
        document.getElementById('client-id').value = data.id;
    });

    $('.waiter-select').select2({
        placeholder: 'Buscar mesero',
        ajax: {
            url: '/app/venta/meseros_api/',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return { term: params.term };
            },
            processResults: function (data) {
                return {
                    results: data.map(mesero => ({
                        id: mesero.id,
                        text: `${mesero.nombre} - ${mesero.tipo_documento}: ${mesero.numero_documento}`,
                    }))
                };
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('Error:', textStatus, errorThrown);
            },
            cache: true
        }
    }).on('select2:select', function (e) {
        const data = e.params.data;
        $(this).data('select2').$container.find('.select2-selection__placeholder').text(data.text);
    });

    function prepareForm(event) {
        event.preventDefault();
    
        const dineroRecibido = parseFloat(dineroRecibidoInput.value) || 0;
        const subtotal = parseFloat(subtotalElement.textContent.replace('$', '')) || 0;
    
        if (dineroRecibido < subtotal) {
            Swal.fire({
                title: 'Error!',
                text: 'El dinero recibido no puede ser menor al total de la venta.',
                icon: 'error',
            });
            return;
        }
    
        const clientId = $('#client-select').val();
        if (!clientId) {
            Swal.fire({
                title: 'Error!',
                text: 'Debes agregar un cliente.',
                icon: 'error',
            });
            return;
        }
    
        const waiterId = $('#waiter-select').val();
        if (!waiterId) {
            Swal.fire({
                title: 'Error!',
                text: 'Debes seleccionar un mesero.',
                icon: 'error',
            });
            return;
        }


        if (!validateInputs()) {
            Swal.fire({
                title: 'Error!',
                text: 'No se puede guardar la venta sin al menos un producto o plato.',
                icon: 'error',
            });
            return;
        }
    
        const detallesVenta = [];
        document.querySelectorAll('#product-rows tr').forEach(row => {
            const idProducto = $(row.querySelector('.product-select')).val();
            const cantidadProducto = row.querySelector('.product-quantity').value;
            const precioProducto = row.querySelector('.product-price').value;
            const subtotalVenta = (cantidadProducto * precioProducto).toFixed(2);
    
            detallesVenta.push({
                id_producto: idProducto,
                cantidad_producto: cantidadProducto,
                subtotal_venta: subtotalVenta,
            });
        });
    
        const cuentasData = [];
        document.querySelectorAll('#dish-rows tr').forEach(row => {
            const idPlato = $(row.querySelector('.dish-select')).val();
            const cantidadPlato = row.querySelector('.dish-quantity').value;
            const precioPlato = row.querySelector('.dish-price').value;
            const subtotalPlato = (cantidadPlato * precioPlato).toFixed(2);
            const idCliente = $('#client-select').val();
            const idMesero = $('#waiter-select').val();
    
            cuentasData.push({
                id_plato: idPlato,
                cantidad_plato: cantidadPlato,
                subtotal_plato: subtotalPlato,
                id_cliente: idCliente,
                id_mesero: idMesero,
            });
        });
    
        const form = document.querySelector('form');
        const formData = new FormData(form);
        formData.append('detalles_venta', JSON.stringify(detallesVenta));
        formData.append('cuentas', JSON.stringify(cuentasData));
    
        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: '¡Éxito!',
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    window.location.href = '/app/venta/listar/';
                });
            } else {
                Swal.fire({
                    title: 'Error',
                    text: data.message,
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error',
                text: 'Ocurrió un error al intentar generar la venta.',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        });
    }
    
    dineroRecibidoInput.addEventListener('input', calculateChange);
    document.querySelector('form').addEventListener('submit', prepareForm);
    productRows.addEventListener('input', validateInputs);
    dishRows.addEventListener('input', validateInputs);

    addProductRow();
    addDishRow();

    window.addProductRow = addProductRow;
    window.addDishRow = addDishRow;
});

// VENTA DE CAJA //
document.addEventListener('DOMContentLoaded', function () {
    const productRows = document.getElementById('product-sale-rows');
    const subtotalElement = document.getElementById('subtotal_sale');
    const dineroRecibidoInput = document.getElementById('money_received_sale');
    const cambioElement = document.getElementById('change_sale');
    let validationTimeout = null;

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
                <i type="button" class="delete-row fas fa-trash-alt" style="color: #04644B; font-size: 25px;"
                    onmouseover="this.style.color='#ff0000';"
                    onmouseout="this.style.color='#04644B';"></i>
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
                            text:`${producto.producto} - ${producto.id_presentacion__presentacion} (${producto.id_presentacion__unidad_medida})`,
                            valor: producto.valor,
                            cantidad: producto.cantidad
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
            
            priceInput.value = data.valor || 0;
            stockSpan.textContent = data.cantidad || 0;
            quantityInput.max = data.cantidad || 0;
            quantityInput.value = 1; 

            $(this).data('select2').$container.find('.select2-selection__placeholder').text(data.text);

            updateStockColor(stockSpan, data.cantidad);

            validateInputs();
        });

        productRows.appendChild(row);

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
    }

    function validateInputs() {
        let isValid = true;
        let ids = new Set();
        let subtotal = 0;
        let duplicateError = false;

        document.querySelectorAll('#product-sale-rows tr').forEach(row => {
            const select = $(row.querySelector('.product-select')).val();
            const quantityInput = row.querySelector('.product-quantity');
            const priceInput = row.querySelector('.product-price');
            const stockSpan = row.querySelector('.product-stock');

            const quantity = Number(quantityInput.value);
            const price = Number(priceInput.value);
            const maxQuantity = Number(quantityInput.max);

            if (ids.has(select)) {
                $(row.querySelector('.product-select')).next().addClass('error');
                isValid = false;
                duplicateError = true;
            } else {
                $(row.querySelector('.product-select')).next().removeClass('error');
                ids.add(select);
            }

            if (quantity <= 0 || quantity > maxQuantity) {
                quantityInput.classList.add('error');
                if (quantity > maxQuantity) {
                    Swal.fire({
                        title: 'Advertencia!',
                        text: `La cantidad ingresada (${quantity}) supera el stock disponible (${maxQuantity}).`,
                        icon: 'warning',
                    });
                }
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
        });

        subtotalElement.textContent = `$${subtotal.toFixed(2)}`;

        if (duplicateError) {
            Swal.fire({
                title: 'Error!',
                text: 'No se pueden guardar productos duplicados.',
                icon: 'error',
            });
        }

        return isValid && !duplicateError;
    }

    function calculateChange() {
        const dineroRecibido = parseFloat(dineroRecibidoInput.value) || 0;
        const subtotal = parseFloat(subtotalElement.textContent.replace('$', '')) || 0;
        const cambio = dineroRecibido - subtotal;

        cambioElement.value = cambio.toFixed(2);
    }

    function prepareForm(event) {
        event.preventDefault();
    
        if (!validateInputs()) {
            return;
        }
    
        const dineroRecibido = parseFloat(dineroRecibidoInput.value) || 0;
        const subtotal = parseFloat(subtotalElement.textContent.replace('$', '')) || 0;
    
        if (dineroRecibido < subtotal) {
            Swal.fire({
                title: 'Error!',
                text: 'El dinero recibido no puede ser menor al total de la venta.',
                icon: 'error',
            });
            return;
        }
    
        const detallesVenta = [];
        let productosLista = '';
    
        document.querySelectorAll('#product-sale-rows tr').forEach(row => {
            const idProducto = $(row.querySelector('.product-select')).val();
            const productoText = $(row.querySelector('.product-select')).text();
            const cantidadProducto = row.querySelector('.product-quantity').value;
            const subtotalVenta = row.querySelector('.product-total').textContent.replace('$', '').trim();
    
            detallesVenta.push({
                id_producto: idProducto,
                cantidad_producto: cantidadProducto,
                subtotal_venta: parseFloat(subtotalVenta.replace('$', '')) || 0
            });
    
            productosLista += `<li>${productoText} - Cantidad: ${cantidadProducto} - Subtotal: $${subtotalVenta}</li>`;
        });
    
        const detallesVentaJSON = JSON.stringify(detallesVenta);
        document.getElementById('detalles_venta').value = detallesVentaJSON;
    
        const form = document.querySelector('form');
        const formData = new FormData(form);
    
        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: '¡Éxito!',
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    window.location.href = '/app/venta/listar/';
                });
            } else {
                Swal.fire({
                    title: 'Error',
                    text: data.message,
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error',
                text: 'Ocurrió un error al intentar generar la venta.',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        });
    }
    
    dineroRecibidoInput.addEventListener('input', calculateChange);

    document.querySelector('form').addEventListener('submit', prepareForm);

    productRows.addEventListener('input', validateInputs);

    addProductSaleRow();

    window.addProductSaleRow = addProductSaleRow;
});

// CLIENTES //
document.addEventListener('DOMContentLoaded', function () {
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            const csrftoken = getCookie('csrftoken');
    
            if (!csrftoken) {
                throw new Error('CSRF token not found.');
            }
    
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    });

    $('#save-client').on('click', function() {
        console.log("Botón de guardar cliente presionado");
        
        var formData = new FormData($('#clienteForm')[0]);
        formData.forEach(function(value, key) {
        console.log(key + ": " + value);
        });
    
        $.ajax({
            url: '/app/venta/crear_cliente_ajax/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        title: 'Registro exitoso',
                        text: 'Cliente creado existosamente.',
                        icon: 'success',
                    });
                    $('#clienteSelector').append(new Option(response.cliente_nombre, response.cliente_id));
                    $('#modal').modal('hide');
                } else {
                    $('.is-invalid').removeClass('is-invalid');
                    $('.invalid-feedback').remove();
    
                    var errors = response.errors;
                    for (var field in errors) {
                        var fieldElement = $('[name=' + field + ']');
                        fieldElement.addClass('is-invalid');
    
                        var errorElement = $('<div class="invalid-feedback">' + errors[field] + '</div>');
                        fieldElement.after(errorElement);
                    }
                }
            },
            error: function(xhr, errmsg, err) {
                console.log("Error al crear el cliente: " + errmsg);
            }
       });
    });
});