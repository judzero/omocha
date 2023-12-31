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

var customerorder = [];
var DictProd = {};
var DictPrice = {};
// An array to store all AJAX requests
var ajaxRequests = [];

document
  .getElementById("proceedToCheckoutBtn")
  .addEventListener("click", (event) => {
    event.preventDefault();

    console.log("Button clicked!");

    var productsToOrder = [];

    $(".item-checkbox:checked").each(function () {
      var tableRow = $(this).closest("tr");
      var productName = tableRow.find(".product-name").text();
      var price = parseFloat(tableRow.data("price"));
      var quantity = parseInt(tableRow.find(".quantity").text());

      var productDetails = {
        price: price,
        quantity: quantity,
      };

      // Create DictProd entry with productName as the key
      DictProd[productName] = {};
      DictPrice[productName] = {};

      customerorder.push({
        [productName]: productDetails,
      });

      DictProd[productName] = productDetails;

      updateValues(customerorder, productName, productDetails);
      console.log(
        "Data being sent:",
        JSON.stringify({
          productName,
          DictProd: DictProd[productName],
        })
      );

      productsToOrder.push({
        productName: productName,
        ProdInfo: DictProd[productName],
      });

      obj = DictProd;
      console.log("Keys and Values:");
      Object.keys(obj).forEach(function (key) {
        console.log(key + ": " + JSON.stringify(obj[key]));
      });

      var ajaxRequest = $.ajax({
        type: "POST",
        url: "/customer/order",
        contentType: "application/json",
        data: JSON.stringify({
          products: productsToOrder,
        }),
        dataType: "json",
        success: function (response) {
          console.log("Success:", response.message);
          DictProd[productName] = { id: response.productId };
        },
        error: function (xhr, status, error) {
          console.log("Error:", error);
          if (xhr.responseJSON && xhr.responseJSON.error) {
            alert("Error: " + xhr.responseJSON.error);
          } else {
            alert("Please Log in first.");
          }
        },
      });

      ajaxRequests.push(ajaxRequest);
    });

    // Wait for all AJAX requests to complete
    Promise.all(ajaxRequests)
      .then(function () {
        var updatedObjectAsString = JSON.stringify(customerorder);
        console.log("customerorder after AJAX:", updatedObjectAsString);
      })
      .catch(function (error) {
        console.log("Error in AJAX requests:", error);
      });
  });

function updateValues(array, key, value) {
  var existingProduct = array.find(function (item) {
    return item[key] !== undefined;
  });

  if (existingProduct) {
    existingProduct[key] = value;
  } else {
    var product = {};
    product[key] = value;
    array.push(product);
  }
}

// JALIFOGO TEST
