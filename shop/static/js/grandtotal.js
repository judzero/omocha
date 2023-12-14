$(document).ready(function () {
    $('#showGrandTotalCheckbox').change(function () {
        $('#grandTotal').toggle(this.checked);
    });

    $('.item-checkbox').change(function () {
        updateGrandTotal();
        countCheckedCheckboxes();
    });

    $('.remove-btn').click(function () {
        $(this).closest('tr').remove();
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
        if ($('.item-checkbox:checked').length > 0) {
            // Set shipping to $50 when at least one checkbox is checked
            shipping = 50;
        }

        $('.item-checkbox:checked').each(function () {
            var price = parseFloat($(this).closest('tr').data('price'));
            var discount = parseFloat($(this).closest('tr').data('discount'));
            var subtotal = parseFloat($(this).data('subtotal'));

            if (isNaN(price) || isNaN(discount) || isNaN(subtotal)) {
                return;
            }

            total += (subtotal - (discount / 100) * price);
        });

        grandtotal = total + shipping;

        $('#subTotalValue').text('$' + total.toFixed(2));
        $('#grandTotalValue').text('$' + grandtotal.toFixed(2));
        $('#shippingValue').text('$' + shipping.toFixed(2));
    }

    function countCheckedCheckboxes() {
        var checkedCount = $('.item-checkbox:checked').length;
        $('#checkboxCount').text(checkedCount);
    }

    function checkItemQuantities() {
        $('.product-quantity').each(function () {
            var quantity = parseInt($(this).closest('tr').data('quantity'));
            if (quantity === 1) {
                // Disable the input field or add some visual indication
                $(this).prop('disabled', true);
            }
        });
    }
});
