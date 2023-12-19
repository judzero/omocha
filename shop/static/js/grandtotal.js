$(document).ready(function () {
  $("#showGrandTotalCheckbox").change(function () {
    $("#grandTotal").toggle(this.checked);
  });

  $(".item-checkbox").change(function () {
    updateGrandTotal();
    countCheckedCheckboxes();

    // Retrieve product details when checkbox is checked
    if ($(this).is(":checked")) {
      var tableRow = $(this).closest("tr");

      var productName = tableRow.find(".product-name").text();
      var price = parseFloat(tableRow.data("price"));
      var quantity = parseInt(tableRow.find(".quantity").text());

      // Log or use the values as needed
      console.log("Product Name:", productName);
      console.log("Price:", price);
      console.log("Quantity:", quantity);
    }
  });

  $(".remove-btn").click(function () {
    $(this).closest("tr").remove();
    updateGrandTotal();
    countCheckedCheckboxes();
  });

  // Initialize grand total, checkbox count, and item quantity on page load
  updateGrandTotal();
  countCheckedCheckboxes();
  checkItemQuantities();

  function updateGrandTotal() {
    var total = 0;
    var shipping = 0;
    var grandtotal = 0;

    // Check if at least one checkbox is checked
    if ($(".item-checkbox:checked").length > 0) {
      // Set shipping to $50 when at least one checkbox is checked
      shipping = 50;
    }

    $(".item-checkbox:checked").each(function () {
      var price = parseFloat($(this).closest("tr").data("price"));
      var discount = parseFloat($(this).closest("tr").data("discount"));
      var subtotal = parseFloat($(this).data("subtotal"));

      if (isNaN(price) || isNaN(discount) || isNaN(subtotal)) {
        return;
      }

      total += subtotal - (discount / 100) * price;
    });

    grandtotal = total + shipping;

    $("#subTotalValue").text("$" + total.toFixed(2));
    $("#grandTotalValue").text("$" + grandtotal.toFixed(2));
    $("#shippingValue").text("$" + shipping.toFixed(2));
  }

  function countCheckedCheckboxes() {
    var checkedCount = $(".item-checkbox:checked").length;
    $("#checkboxCount").text(checkedCount);
  }

  function checkItemQuantities() {
    $(".product-quantity").each(function () {
      var quantity = parseInt($(this).closest("tr").data("quantity"));
      if (quantity === 1) {
        // Disable the input field or add some visual indication
        $(this).prop("disabled", true);
      }
    });
  }
});

document
  .getElementById("proceedToCheckoutBtn")
  .addEventListener("click", (event) => {
    event.preventDefault(); // Prevent the default behavior of the button

    console.log("Button clicked!");

    var customerorder = [];

    function updateValues(orderArray, key, items) {
      var newObject = {};
      newObject[key] = items;

      orderArray.push(newObject);
    }

    // Collect order details for each checked checkbox
    $(".item-checkbox:checked").each(function () {
      var tableRow = $(this).closest("tr");
      var productName = tableRow.find(".product-name").text();
      var price = parseFloat(tableRow.data("price"));
      var quantity = parseInt(tableRow.find(".quantity").text());

      updateValues(customerorder, productName, {
        price: price,
        quantity: quantity,
      });
    });

    var objectAsString = JSON.stringify(customerorder);
    console.log(objectAsString);
    // Log or use the values as needed

    customerorder.forEach(function (product) {
      Object.keys(product).forEach(function (key) {
        var productDetails = product[key];
        var price = productDetails.price;
        var quantity = productDetails.quantity;

        $.ajax({
          type: "POST",
          url: "/customer/order",
          contentType: "application/json",
          data: JSON.stringify({
            productName: key, // Use the actual key as the product name
            price: price,
            quantity: quantity,
          }),
          dataType: "json",
          success: function (response) {
            console.log("Success:", response.message);
            // Add code for any actions dependent on a successful response
          },
          error: function (xhr, status, error) {
            console.log("Error:", error);
            // Add code to handle and display the error to the user
            if (xhr.responseJSON && xhr.responseJSON.error) {
              alert("Error: " + xhr.responseJSON.error);
            } else {
              alert("Unexpected error occurred.");
            }
          },
        });
      });
    });
  });
