# Chính Sách Mua Sắm Mock Cho Lab Multi-Agent

> Tài liệu này là **mock data phục vụ giảng dạy**. Nội dung được **biên soạn lại theo phong cách chính sách của các sàn TMĐT lớn** như Shopee, TikTok Shop, Tiki và Lazada để sinh viên thực hành RAG, tool calling và multi-agent. Đây **không phải** là chính sách chính thức của bất kỳ sàn nào.

## 1. Mục đích tài liệu

Tài liệu này mô tả các quy định mẫu dành cho một nền tảng mua sắm online giả lập tên là **VinShop Demo**. Mục tiêu là tạo ra một nguồn dữ liệu đủ dài, đủ chi tiết và có cấu trúc rõ ràng để:

- dùng làm knowledge base cho `Policy / RAG Agent`
- dùng để trích xuất câu trả lời có citation theo từng mục
- kết hợp với dữ liệu đơn hàng thực tế để trả lời các câu hỏi hỗn hợp

Ví dụ:

- "Chính sách hoàn trả hàng ra sao?"
- "Đơn hàng 1971 có được hoàn trả không?"
- "Voucher có được hoàn lại khi hủy đơn không?"
- "Giao hàng hỏa tốc mất bao lâu?"

## 2. Phạm vi áp dụng

Chính sách này áp dụng cho:

- khách hàng mua sắm trên nền tảng VinShop Demo
- nhà bán hàng tham gia nền tảng
- các đơn vị vận chuyển tích hợp trong hệ thống
- bộ phận chăm sóc khách hàng và vận hành sau bán

Chính sách áp dụng cho ba nhóm nghiệp vụ chính:

- giao hàng và theo dõi đơn hàng
- đổi trả, hoàn tiền, khiếu nại sau bán
- voucher, khuyến mãi và các ưu đãi liên quan

## 3. Thuật ngữ

### 3.1. Đơn hàng hợp lệ

Đơn hàng hợp lệ là đơn được tạo thành công trên hệ thống, có mã đơn hàng rõ ràng, thông tin nhận hàng đầy đủ và không vi phạm quy định chống gian lận.

### 3.2. Giao hàng thành công

Đơn được xem là giao hàng thành công khi hệ thống vận chuyển cập nhật trạng thái `delivered` hoặc tương đương, và hàng hóa đã tới đúng địa chỉ hoặc đúng người nhận được ủy quyền.

### 3.3. Yêu cầu trả hàng / hoàn tiền

Là yêu cầu do khách hàng khởi tạo sau khi đơn hàng đã phát sinh vấn đề như:

- giao sai sản phẩm
- thiếu hàng
- hàng lỗi, vỡ, hư hỏng
- hàng không đúng mô tả
- nghi ngờ hàng giả hoặc sai thương hiệu
- đơn đã giao nhưng khách có nhu cầu đổi ý trong phạm vi cho phép

### 3.4. Voucher nền tảng

Voucher nền tảng là ưu đãi do VinShop Demo hoặc đối tác tài trợ, áp dụng theo điều kiện từng chiến dịch.

### 3.5. Voucher shop

Voucher shop là ưu đãi do nhà bán hàng phát hành, chỉ áp dụng cho sản phẩm hoặc gian hàng tương ứng.

### 3.6. Voucher vận chuyển

Voucher vận chuyển là mã giảm phí giao hàng, có thể áp dụng độc lập hoặc kết hợp với các loại voucher khác tùy điều kiện chương trình.

## 4. Chính sách giao hàng

### 4.1. Phương thức giao hàng

VinShop Demo hỗ trợ các hình thức giao hàng sau:

- `standard`: giao hàng tiêu chuẩn toàn quốc
- `fast`: giao nhanh nội thành hoặc liên tỉnh ngắn
- `express`: giao ưu tiên cho sản phẩm đủ điều kiện
- `scheduled`: giao theo khung giờ hẹn trước tại một số khu vực

Không phải mọi sản phẩm đều hỗ trợ tất cả phương thức giao hàng. Hệ thống sẽ chỉ hiển thị các phương thức phù hợp dựa trên:

- địa chỉ nhận hàng
- kích thước và khối lượng gói hàng
- điều kiện đóng gói của nhà bán
- đặc thù sản phẩm như dễ vỡ, hàng giá trị cao, hàng cồng kềnh hoặc hàng cần bảo quản đặc biệt

### 4.2. Thời gian xử lý đơn

Sau khi khách đặt hàng thành công, nhà bán hoặc kho vận hành sẽ cần một khoảng thời gian để:

- xác nhận tồn kho
- đóng gói
- in vận đơn
- bàn giao cho đơn vị vận chuyển

Thời gian xử lý thông thường:

- đơn tiêu chuẩn: từ 4 đến 24 giờ làm việc
- đơn giao nhanh: từ 1 đến 6 giờ làm việc nếu đặt trong khung giờ hỗ trợ
- đơn có nhiều kiện hoặc nhiều shop: có thể tách thành nhiều gói và xử lý độc lập

### 4.3. Thời gian giao hàng dự kiến

Thời gian giao hàng dự kiến phụ thuộc vào khu vực nhận hàng:

- nội thành cùng tỉnh/thành phố lớn: 1 đến 2 ngày
- liên tỉnh khu vực lân cận: 2 đến 4 ngày
- tuyến huyện, xã hoặc khu vực xa: 3 đến 7 ngày
- sản phẩm cồng kềnh hoặc hàng cần kiểm tra đặc biệt: cộng thêm 1 đến 3 ngày

Đây là thời gian dự kiến. Hệ thống có thể điều chỉnh `estimated_delivery` nếu phát sinh:

- thời tiết xấu
- ùn tắc giao thông
- người nhận không liên lạc được
- sai hoặc thiếu thông tin địa chỉ
- hàng phải trung chuyển nhiều chặng

### 4.4. Giao hàng nhanh và giao ưu tiên

Đối với đơn đủ điều kiện giao nhanh hoặc giao ưu tiên:

- khách cần đặt trong khung giờ hệ thống hỗ trợ
- địa chỉ nhận phải nằm trong vùng phục vụ
- sản phẩm không thuộc danh mục hạn chế vận chuyển

Các đơn giao nhanh có thể bị chuyển sang giao tiêu chuẩn nếu:

- shop bàn giao hàng chậm
- sản phẩm vượt ngưỡng kích thước hoặc khối lượng cho phép
- phát sinh rủi ro vận hành từ đơn vị vận chuyển

### 4.5. Tách đơn và giao nhiều kiện

Một đơn hàng có thể được tách thành nhiều kiện trong các trường hợp:

- đơn có sản phẩm từ nhiều nhà bán khác nhau
- các mặt hàng nằm ở nhiều kho
- một phần hàng sẵn kho, phần còn lại cần xử lý riêng

Khi đó:

- mỗi kiện có thể có mã vận đơn riêng
- thời gian giao của từng kiện có thể khác nhau
- việc hoàn trả cũng có thể phát sinh theo từng kiện hoặc từng sản phẩm

### 4.6. Kiểm hàng khi nhận

Khách hàng được khuyến nghị:

- kiểm tra tình trạng thùng hàng khi nhận
- quay video mở kiện đối với sản phẩm giá trị cao
- báo ngay trên ứng dụng nếu phát hiện vỡ, móp, thiếu phụ kiện hoặc sai sản phẩm

Trong phạm vi nghiệp vụ mô phỏng cho lab:

- khách được phép kiểm tra ngoại quan gói hàng trước khi xác nhận nhận
- việc dùng thử sâu, lắp đặt, kích hoạt hoặc sử dụng lâu dài không thuộc phạm vi "kiểm hàng tại chỗ"

### 4.7. Giao hàng không thành công

Đơn hàng có thể bị cập nhật `delivery_failed` khi:

- người nhận không nghe máy sau nhiều lần liên hệ
- địa chỉ giao không chính xác
- người nhận hẹn lại nhiều lần vượt quá ngưỡng hỗ trợ
- khách từ chối nhận hàng không có lý do phù hợp
- khu vực giao hàng tạm thời bị hạn chế

Trong trường hợp giao không thành công:

- hệ thống có thể tự động lên lịch giao lại
- hoặc chuyển hoàn về kho / shop
- hoặc hủy đơn tùy trạng thái thanh toán và điều kiện vận hành

## 5. Chính sách đổi trả và hoàn tiền

### 5.1. Điều kiện chung để gửi yêu cầu

Khách hàng có thể gửi yêu cầu trả hàng / hoàn tiền khi có căn cứ hợp lý và còn trong thời hạn hỗ trợ của hệ thống.

Trong bộ mock policy này, thời hạn mặc định là:

- tối đa **15 ngày kể từ khi đơn cập nhật giao hàng thành công** đối với đa số ngành hàng thông thường
- tối đa **3 ngày** đối với hàng tiêu dùng nhanh, mỹ phẩm dùng thử, thực phẩm hoặc sản phẩm có rủi ro vệ sinh cao
- tối đa **24 giờ** đối với hàng tươi sống hoặc hàng có điều kiện bảo quản đặc biệt

Thời hạn cụ thể có thể được ghi đè ở dữ liệu sản phẩm hoặc dữ liệu đơn hàng bằng các trường như:

- `return_window_days`
- `returnable`
- `eligible_for_return_until`

### 5.2. Các lý do được chấp nhận

Yêu cầu sau bán có thể được xem xét khi thuộc một hoặc nhiều lý do sau:

- sản phẩm bị bể, vỡ, móp, rách hoặc hư hỏng do vận chuyển
- sản phẩm bị lỗi kỹ thuật
- giao sai phân loại, sai màu, sai kích cỡ hoặc sai mẫu
- thiếu phụ kiện, thiếu quà tặng kèm, thiếu số lượng
- sản phẩm không đúng mô tả quan trọng trên trang bán
- nghi ngờ hàng giả, hàng nhái, sai xuất xứ
- đơn giao trễ nghiêm trọng dẫn đến khách không còn nhu cầu nhận
- khách đổi ý trong thời hạn cho phép của từng ngành hàng

### 5.3. Các trường hợp không hỗ trợ trả hàng

Để phù hợp với một hệ thống thương mại điện tử thực tế, các trường hợp sau thường bị giới hạn hoặc không hỗ trợ trả hàng:

- sản phẩm tiêu dùng đã mở niêm phong và không còn khả năng bán lại
- thực phẩm tươi sống hoặc hàng đông lạnh sau khi đã giao thành công
- đồ lót, sản phẩm chăm sóc cá nhân, mỹ phẩm đã qua sử dụng
- phần mềm, thẻ quà tặng điện tử, mã nạp điện tử
- hàng đặt riêng, cá nhân hóa theo yêu cầu
- sản phẩm bị hư hỏng do khách sử dụng sai hướng dẫn
- khách gửi lại sai hàng, thiếu phụ kiện hoặc không đúng serial

Các trường hợp trên vẫn có thể được hỗ trợ hoàn tiền một phần hoặc xử lý ngoại lệ nếu có quyết định từ bộ phận chăm sóc khách hàng.

### 5.4. Bằng chứng cần cung cấp

Khi gửi yêu cầu trả hàng / hoàn tiền, khách nên cung cấp đầy đủ:

- ảnh chụp kiện hàng còn nguyên tem vận chuyển
- video mở kiện nếu có
- ảnh chụp sản phẩm lỗi hoặc hư hỏng
- ảnh chụp tem serial, mã vạch hoặc phụ kiện đi kèm
- mô tả ngắn gọn vấn đề gặp phải

Nếu bằng chứng chưa đủ rõ:

- hệ thống có thể yêu cầu bổ sung
- thời gian xử lý có thể bị kéo dài
- yêu cầu có thể bị từ chối nếu không đủ căn cứ

### 5.5. Trình tự xử lý yêu cầu

Quy trình xử lý mẫu trong lab:

1. Khách tạo yêu cầu trên ứng dụng
2. Hệ thống ghi nhận lý do và bằng chứng
3. Nhà bán hoặc bộ phận vận hành phản hồi vòng đầu
4. Nếu cần trả hàng, khách chọn hình thức gửi trả
5. Hệ thống xác nhận trạng thái hàng trả về
6. Hoàn tiền được thực hiện sau khi yêu cầu được chấp thuận

### 5.6. Thời gian phản hồi và thời gian gửi trả

Để đơn giản hóa cho lab, có thể áp dụng các mốc sau:

- phản hồi ban đầu của nhà bán hoặc hệ thống: trong vòng 48 giờ
- thời gian khách phải gửi hàng sau khi yêu cầu được chấp nhận: trong vòng 5 ngày lịch
- thời gian xử lý hoàn tiền sau khi hệ thống xác nhận yêu cầu hợp lệ: từ 3 đến 7 ngày làm việc

### 5.7. Hình thức gửi trả

Khách có thể gửi trả theo một trong các hình thức:

- `drop_off`: mang hàng tới bưu cục đối tác
- `pickup`: đơn vị vận chuyển đến lấy hàng tại nhà
- `self_arranged`: khách tự sắp xếp đơn vị vận chuyển

Đối với hình thức `self_arranged`, khách cần giữ lại:

- biên nhận gửi hàng
- mã vận đơn
- thông tin người nhận hàng hoàn

### 5.8. Chi phí vận chuyển chiều hoàn

Nguyên tắc mock cho lab:

- nếu lỗi thuộc nhà bán, hệ thống hoặc đơn vị vận chuyển: khách không chịu phí trả hàng
- nếu khách đổi ý theo chính sách cho phép: khách có thể cần ứng trước phí hoặc chịu một phần phí
- nếu khách tự chọn hình thức `self_arranged`: việc hoàn lại phí phụ thuộc vào nguyên nhân và bằng chứng hợp lệ

### 5.9. Hoàn tiền

Tiền hoàn có thể được trả về:

- ví nội bộ của nền tảng
- tài khoản ngân hàng
- thẻ thanh toán
- phương thức thanh toán gốc nếu hạ tầng thanh toán hỗ trợ

Thời gian nhận tiền thực tế có thể phụ thuộc:

- cổng thanh toán
- ngân hàng phát hành
- trạng thái đối soát
- việc xác minh chứng từ của bộ phận vận hành

### 5.10. Quan hệ giữa trạng thái đơn hàng và quyền trả hàng

Trong dữ liệu lab, sinh viên nên hiểu rõ:

- đơn chưa giao thành công thường **chưa thể** bắt đầu quy trình trả hàng thông thường
- đơn đang `in_transit` có thể được hỗ trợ hủy hoặc từ chối nhận trong một số trường hợp, nhưng không xem là "đã trả hàng"
- đơn `delivered` mới là trạng thái thường dùng để tính cửa sổ đổi trả
- đơn `completed` vẫn có thể còn trong hạn trả hàng nếu chưa vượt `eligible_for_return_until`

Điều này rất quan trọng cho các câu hỏi như:

- "Đơn hàng 1971 có được hoàn trả không?"

## 6. Chính sách voucher và khuyến mãi

### 6.1. Các loại voucher trong hệ thống

Hệ thống mock hỗ trợ các loại voucher sau:

- voucher nền tảng
- voucher shop
- voucher vận chuyển
- voucher hoàn xu / cashback
- voucher bù dịch vụ hoặc voucher chăm sóc khách hàng

### 6.2. Điều kiện áp dụng cơ bản

Mỗi voucher có thể có các điều kiện như:

- giá trị đơn hàng tối thiểu
- ngành hàng áp dụng
- thời gian hiệu lực
- số lượt dùng tối đa
- giới hạn theo từng tài khoản
- không áp dụng đồng thời với một số ưu đãi khác

Ví dụ các trường dữ liệu liên quan trong JSON:

- `voucher_type`
- `discount_type`
- `discount_value`
- `min_order_value`
- `max_discount`
- `remaining_uses`
- `stackable_with`

### 6.3. Quy tắc cộng dồn voucher

Trong mock policy này, một đơn hàng có thể dùng tối đa:

- 01 voucher nền tảng
- 01 voucher shop
- 01 voucher vận chuyển

Không phải mọi tổ hợp đều hợp lệ. Hệ thống sẽ tự tính theo quy tắc:

1. áp dụng ưu đãi của shop trước
2. áp dụng voucher nền tảng tiếp theo
3. cuối cùng mới tính ưu đãi vận chuyển

### 6.4. Giới hạn voucher theo hạng khách hàng

Để tạo dữ liệu đủ thực tế cho lab, nền tảng giả lập áp dụng hạn mức voucher mỗi tháng theo hạng thành viên:

| Hạng khách hàng | Số voucher tối đa / tháng |
| --- | ---: |
| Standard | 6 |
| Silver | 8 |
| Gold | 10 |
| Platinum | 12 |
| VIP | 15 |

Trong dữ liệu khách hàng, trường `max_voucher_per_month` sẽ phản ánh hạn mức này.

### 6.5. Hoàn lại voucher khi đơn bị hủy

Khi đơn hàng bị hủy, voucher có thể được hoàn lại nếu thỏa các điều kiện sau:

- voucher còn hiệu lực
- voucher chưa vượt giới hạn sử dụng
- toàn bộ đơn hoặc toàn bộ phần sử dụng chung voucher đã bị hủy
- voucher không thuộc nhóm chiến dịch bị loại trừ

Các trường hợp thường **không** được hoàn lại:

- voucher số lượng giới hạn đã hết lượt
- voucher livestream đã hết hiệu lực
- voucher video / flash campaign hết lượt sử dụng
- voucher phát hành cho sự kiện đặc biệt và có quy định không hoàn

### 6.6. Voucher sau trả hàng / hoàn tiền

Nếu yêu cầu trả hàng / hoàn tiền được chấp nhận:

- voucher đã dùng có thể được hoàn lại, cấp lại, hoặc không hoàn lại tùy điều kiện chiến dịch
- mã bù có thể được cấp riêng thay vì hoàn đúng voucher cũ
- một số voucher chỉ được hoàn khi hoàn tiền toàn phần

### 6.7. Thu hồi voucher và chống gian lận

Nền tảng có quyền khóa hoặc thu hồi voucher trong các trường hợp:

- tạo nhiều tài khoản để săn mã
- tự mua tự hủy nhiều lần bất thường
- lợi dụng lỗi hệ thống để cộng dồn ưu đãi trái quy định
- có dấu hiệu thông đồng giữa người mua và nhà bán

## 7. Hỗ trợ khách hàng và khiếu nại

### 7.1. Các kênh hỗ trợ

Khách hàng có thể liên hệ:

- chat trong ứng dụng
- hotline chăm sóc khách hàng
- email hỗ trợ
- biểu mẫu khiếu nại sau bán

### 7.2. Thông tin cần cung cấp khi yêu cầu hỗ trợ

Để hệ thống hoặc agent trả lời chính xác hơn, khách nên cung cấp:

- mã đơn hàng
- mã khách hàng hoặc số điện thoại đã đăng ký
- sản phẩm cần hỗ trợ
- nội dung vấn đề
- ảnh hoặc video nếu có

### 7.3. Các tình huống cần hỏi làm rõ

Response Agent nên ưu tiên hỏi lại khi thiếu các thông tin sau:

- chưa có `order_id`
- chưa có `customer_id`
- khách hỏi chung chung về voucher nhưng không nêu tài khoản
- khách hỏi tình trạng giao hàng nhưng không nói đang hỏi đơn nào
- khách hỏi "có đổi trả được không" nhưng không nêu sản phẩm hoặc thời điểm giao

Ví dụ câu clarification:

- "Anh/chị vui lòng cung cấp mã đơn hàng để em kiểm tra chính xác."
- "Anh/chị muốn xem voucher của khách hàng nào ạ?"
- "Đơn đã giao thành công chưa hay vẫn đang trên đường vận chuyển?"

## 8. Quy định chống gian lận

Nền tảng có thể tạm khóa giao dịch hoặc từ chối hỗ trợ ưu đãi nếu phát hiện:

- địa chỉ nhận hàng ảo hoặc lặp bất thường
- nhiều đơn tự hủy liên tiếp để săn voucher
- trả hàng sai sản phẩm
- cung cấp bằng chứng chỉnh sửa hoặc không trung thực
- khiếu nại lặp lại với tần suất bất thường mà không có cơ sở

Việc phát hiện gian lận có thể dẫn tới:

- khóa voucher
- tạm ngưng ưu đãi
- từ chối hoàn phí vận chuyển
- đánh dấu tài khoản cần kiểm tra thủ công

## 9. Hướng dẫn dùng file này cho lab

Sinh viên có thể chia file này thành các chunk theo:

- tiêu đề cấp 2 và cấp 3
- nhóm chủ đề `giao hàng`, `đổi trả`, `voucher`, `hỗ trợ`

Các câu hỏi phù hợp cho `Policy / RAG Agent`:

- "Chính sách hoàn trả là gì?"
- "Tối đa được dùng mấy voucher mỗi tháng?"
- "Đơn đang giao có trả hàng ngay được không?"
- "Nếu hủy đơn thì voucher có được hoàn lại không?"
- "Khách tự gửi trả thì có được hỗ trợ phí không?"

Các câu hỏi cần kết hợp với `Order / Customer Lookup Agent`:

- "Đơn hàng 1971 có được hoàn trả không?"
- "Khách hàng C001 còn dùng được bao nhiêu voucher trong tháng?"
- "Đơn 2058 giao chậm thì có thể hủy không?"

## 10. Appendix: nguồn tham khảo để biên soạn mock

Nội dung mock được tham khảo về **cấu trúc chủ đề và các tình huống nghiệp vụ phổ biến**, sau đó viết lại cho mục đích giảng dạy:

- Shopee - Chính sách trả hàng và hoàn tiền
- Shopee - Chính sách vận chuyển
- Shopee - Hoàn lại mã giảm giá khi hủy đơn
- TikTok Shop Seller - Returns and Refunds
- TikTok Shop Seller - Return & Refund Methods
- Tiki - Đổi ý miễn phí trong 30 ngày / hỗ trợ đổi trả
- Tiki - Chính sách kiểm hàng

URL tham khảo:

- https://help.shopee.vn/portal/4/article/77251-CHÍNH-SÁCH-TRẢ-HÀNG-VÀ-HOÀN-TIỀN
- https://help.shopee.vn/portal/4/article/77250
- https://help.shopee.vn/portal/4/article/79148
- https://seller-vn.tiktok.com/university/essay?from=policy&identity=1&knowledge_id=1766935302801169&lang=en&role=1
- https://seller-vn.tiktok.com/university/essay?knowledge_id=1398156382422785&lang=en
- https://tiki.vn/thong-tin/tiki-doi-tra-de-dang-an-tam-mua-sam/
- https://tiki.vn/chinh-sach-kiem-hang

Giảng viên có thể yêu cầu sinh viên trích dẫn theo heading, ví dụ:

- `policy_mock_vi.md > 5.10. Quan hệ giữa trạng thái đơn hàng và quyền trả hàng`
- `policy_mock_vi.md > 6.4. Giới hạn voucher theo hạng khách hàng`
- `policy_mock_vi.md > 4.3. Thời gian giao hàng dự kiến`
