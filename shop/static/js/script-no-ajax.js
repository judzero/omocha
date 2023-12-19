var stripe = Stripe(
  "pk_test_51OOkWEK4Yt7azovvDWXIAPJOzZOwq533hXqqZUQGwzQdHZioL4jQrQXTzI8cdeUNyaG1YVVRQuyZ52QFmEhLJksu00EN8c75Kq"
);

const getCheckOut = document.getElementById("proceedToCheckoutBtn");

getCheckOut.addEventListener("click", async (event) => {
  try {
    // Call your backend to create the Checkout Session
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to create checkout session");
    }

    const { id: checkout_session_id } = await response.json();

    // Redirect to Checkout using the Checkout Session ID
    const result = await stripe.redirectToCheckout({
      sessionId: checkout_session_id,
    });

    // If `redirectToCheckout` fails due to a browser or network error,
    // display the localized error message to your customer using `result.error.message`.
    if (result.error) {
      alert(result.error.message);
    }
  } catch (error) {
    console.error("Error initiating checkout:", error.message);
    // Handle the error, e.g., display an error message to the user
  }
});
