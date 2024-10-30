$(document).ready(function () {
    // Gửi yêu cầu kết bạn bằng thẻ <a>
    $('.send-friend-request-btn').on('click', function (event) {
        event.preventDefault(); // Chặn hành động mặc định của thẻ <a>

        let userId = $(this).data('user-id');

        $.ajax({
            url: `/send-friend-request/${userId}/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': window.csrftoken // Thêm CSRF token để bảo mật
            },
            success: function (response) {
                $('#notification-area').html(`<p>${response.message}</p>`);
            },
            error: function (xhr) {
                $('#notification-area').html(`<p>${xhr.responseJSON.message}</p>`);
            }
        });
    });
});
