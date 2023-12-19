var stripe = Stripe(
  pk_test_51OOkWEK4Yt7azovvDWXIAPJOzZOwq533hXqqZUQGwzQdHZioL4jQrQXTzI8cdeUNyaG1YVVRQuyZ52QFmEhLJksu00EN8c75Kq
);

const getCheckOut = document.getElementById("proceedToCheckoutBtn");

getCheckOut.addEventListener("click", (event) => {
  stripe
    .redirectToCheckout({
      // Make the id field from the Checkout Session creation API response
      // available to this file, so you can provide it as parameter here
      // instead of the {{CHECKOUT_SESSION_ID}} placeholder.
      sessionId: checkout_session_id,
    })
    .then(function (result) {
      // If `redirectToCheckout` fails due to a browser or network
      // error, display the localized error message to your customer
      // using `result.error.message`.
    });
});
