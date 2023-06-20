$(document).ready(function() {
    var pageNumber = 1; // Initial page number
    var pageSize = 10; // Number of items to load per page
    var previousScrollTop = 0; // Variable to track the previous scroll position
    var isLoadingTop = false; // Flag to indicate if data is being loaded at the top
    var isLoadingBottom = false; // Flag to indicate if data is being loaded at the bottom
  
    // Initialize the Bootstrap Table
    $('#your-table-id').bootstrapTable({
      url: 'your-data-url',
      method: 'get',
      pagination: false,
      onLoadSuccess: function(data) {
        // Disable the loading indicator after data is loaded
        $('#your-table-id').bootstrapTable('hideLoading');
  
        // Enable the onScroll event if there are more items to load
        if (data.length >= pageSize) {
          $('#your-table-id').on('scroll-body.bs.table', function() {
            var scrollPosition = $(this).scrollTop();
  
            // Check if scrolling up by comparing the previous and current scroll positions
            if (scrollPosition < previousScrollTop) {
              var tableOffsetTop = $(this).find('tbody tr:first').offset().top;
  
              // Check if the scroll position is near the top of the table
              if (scrollPosition <= tableOffsetTop && !isLoadingTop) {
                // Decrement the page number
                pageNumber--;
  
                // Load more data at the top
                loadMoreData('top');
              }
            } else {
              var tableHeight = $(this).height();
              var tableScrollHeight = $(this).find('tbody').get(0).scrollHeight;
  
              // Check if the scroll position is near the bottom of the table
              if (scrollPosition + tableHeight >= tableScrollHeight - 50 && !isLoadingBottom) {
                // Increment the page number
                pageNumber++;
  
                // Load more data at the bottom
                loadMoreData('bottom');
              }
            }
  
            // Update the previous scroll position
            previousScrollTop = scrollPosition;
          });
        }
      }
    });