document.addEventListener('DOMContentLoaded', function() {
    const ratingStars = document.querySelectorAll('.rating .star');
    const currentRating = parseInt(document.querySelector('.rating').getAttribute('data-rating'));

    ratingStars.forEach(star => {
        star.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-value'));
            setRating(value);
        });

        star.addEventListener('mouseover', function() {
            const value = parseInt(this.getAttribute('data-value'));
            highlightStars(value);
        });

        star.addEventListener('mouseout', function() {
            highlightStars(currentRating);
        });
    });

    function setRating(value) {
        currentRating = value;
        highlightStars(value);

        // You can send the rating to the server using AJAX or any other method.
        console.log('Rating selected:', value);
    }

    function highlightStars(value) {
        ratingStars.forEach(star => {
            const starValue = parseInt(star.getAttribute('data-value'));
            star.classList.toggle('active', starValue <= value);
        });
    }
});
