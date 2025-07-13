async function capNhatTinhTrang(monId, tinhTrangMoi) {
    const button = document.getElementById('btnCapNhat' + monId);
    const statusText = document.getElementById('tinhtrang' + monId);

    button.disabled = true;
    button.innerText = 'Đang cập nhật...';

    try {
        const res = await fetch(`/api/cap-nhat-mon/${monId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tinh_trang_moi: tinhTrangMoi })
        });

        if (res.ok) {
            const data = await res.json();


            statusText.innerText = data.tinh_trang ? "Còn món" : "Hết món";
            statusText.className = data.tinh_trang ? "text-success" : "text-danger";


            button.innerText = data.tinh_trang ? "Đánh dấu hết món" : "Đánh dấu còn món";
            button.className = data.tinh_trang ? "btn btn-outline-danger btn-sm w-100" : "btn btn-outline-success btn-sm w-100";


            button.setAttribute("onclick", `capNhatTinhTrang(${monId}, ${!data.tinh_trang})`);
        } else {
            alert("Cập nhật thất bại!");
        }
    } catch (error) {
        alert("Lỗi kết nối server!");
        console.error(error);
    } finally {
        button.disabled = false;
    }
}
