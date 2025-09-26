document.addEventListener("DOMContentLoaded", function () {
  const cartCounter = document.getElementById("cart-counter");

  function updateCartCount() {
    fetch("/cart/count")
      .then((response) => response.json())
      .then((data) => {
        if (data.cart_count !== undefined) {
          cartCounter.textContent = data.cart_count;
        }
      })
      .catch((error) => {
        console.error("Error fetching cart count:", error);
      });
  }

  // Initial cart count update on page load
  updateCartCount();

  const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");
  const toastNotification = document.getElementById("toast-notification");

  addToCartButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const productId = this.dataset.productId;
      fetch("/add_to_cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ product_id: productId }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.cart_count !== undefined) {
            updateCartCount(); // Update cart count after adding a product

            // Show the notification
            toastNotification.classList.add("show");

            // Hide the notification after 3 seconds
            setTimeout(function () {
              toastNotification.classList.remove("show");
            }, 3000);
          }
        })
        .catch((error) => {
          console.error("Error adding to cart:", error);
        });
    });
  });
});