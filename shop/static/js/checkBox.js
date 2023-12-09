$(document).ready(function () {
    // Attach an event listener to the checkbox
    $('#showGrandTotalCheckbox').change(function () {
        // Check if the checkbox is checked
        if ($(this).is(':checked')) {
            // Get the values of all checked checkboxes
            var checkedItems = $('.item-checkbox:checked');

            // Loop through each checked checkbox
            checkedItems.each(function () {
                // Get the data-subtotal attribute value
                var subtotal = $(this).data('subtotal');
                console.log('Subtotal:', subtotal);
                // Add your logic to handle the subtotal value as needed
            });
        }
    });
});
