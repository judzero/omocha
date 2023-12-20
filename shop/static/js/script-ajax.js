stripeKey =
  "pk_test_51OOkWEK4Yt7azovvDWXIAPJOzZOwq533hXqqZUQGwzQdHZioL4jQrQXTzI8cdeUNyaG1YVVRQuyZ52QFmEhLJksu00EN8c75Kq";
var stripe = Stripe(stripeKey);

// Fetch the Checkout Session ID from the server
const fetchCheckoutSession = async () => {
  try {
    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });

    console.log("Raw Response:", response);

    if (!response.ok) {
      throw new Error("Failed to create checkout session");
    }
    const jsonResponse = await response.json();
    console.log("JSON Response:", jsonResponse);

    const { checkout_session_id, checkout_public_key } = jsonResponse;
    console.log("Checkout Session ID:", checkout_session_id);
    console.log("Public Key:", checkout_public_key);

    return { checkout_session_id, checkout_public_key };
  } catch (error) {
    console.error("Error fetching checkout session:", error.message);
    throw error; // Propagate the error to the caller if needed
  }
};

// Handle the click event on the button
const handleCheckoutClick = async () => {
  try {
    const data = await fetchCheckoutSession();
    console.log("Fetched data:", data);

    // Initialize Stripe with the public key
    var stripe = Stripe(data.checkout_public_key);

    // Redirect to Checkout using the Checkout Session ID
    const result = await stripe.redirectToCheckout({
      sessionId: data.checkout_session_id,
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
};

// Attach the click event to the button with ID #proceedToCheckoutBtn
const proceedToCheckoutButton = document.querySelector("#proceedToCheckoutBtn");
proceedToCheckoutButton.addEventListener("click", handleCheckoutClick);
