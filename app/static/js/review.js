document.addEventListener("DOMContentLoaded", function () {
  const reviewForm = document.getElementById("review-form");
  if (reviewForm) {
    reviewForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const productId = window.location.pathname.split("/").pop();
      const rating = document.getElementById("rating").value;
      const text = document.getElementById("review-text").value;

      fetch(`/product/${productId}/add_review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ rating: rating, text: text }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            console.error("Error adding review:", data.error);
            // You could display an error message to the user here
          } else {
            // Create the new review element
            const reviewList = document.getElementById("reviews-list");
            const newReview = document.createElement("div");
            newReview.classList.add("card", "mb-3");
            newReview.innerHTML = `
              <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">${data.author.username} - ${data.created_at}</h6>
                <p class="card-text"><strong>Rating:</strong> ${data.rating}/5</p>
                <p class="card-text">${data.text}</p>
              </div>
            `;

            // Add the new review to the top of the list
            reviewList.prepend(newReview);

            // Clear the form
            reviewForm.reset();

            // Remove the "no reviews" message if it exists
            const noReviewsMessage = reviewList.querySelector("p");
            if (noReviewsMessage && noReviewsMessage.textContent.includes("No reviews yet")) {
              noReviewsMessage.remove();
            }
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  }
});
