document.addEventListener('DOMContentLoaded', function () {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.dataset.productId;
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: productId, quantity: 1 }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.cart_count !== undefined) {
                    const cartCounter = document.getElementById('cart-counter');
                    if (cartCounter) {
                        cartCounter.innerText = data.cart_count;
                    }
                    // Show a toast notification
                    const toast = document.getElementById('toast-notification');
                    toast.innerText = data.message;
                    toast.classList.add('show');
                    setTimeout(() => {
                        toast.classList.remove('show');
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});
