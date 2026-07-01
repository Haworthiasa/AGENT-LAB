---
title: "HAD: Hallucination-Aware Diffusion Priors for 3D Reconstruction"
topic: had
type: blog
date: 2026-06-30
math: katex
highlight: monokai
---

# 1. Tóm tắt

### Bối cảnh

* **3DGS cần nhiều ảnh đầu vào:** Nếu chỉ có ít ảnh, 3DGS thường render ảnh góc nhìn mới bị mờ, méo hình, thiếu chi tiết hoặc sinh floaters.
* **Diffusion giúp sửa ảnh render:** Các hướng như Difix3D dùng diffusion để sửa ảnh render lỗi từ 3DGS, rồi dùng ảnh đã sửa làm ảnh bổ sung để train lại 3DGS.
* **Vấn đề lớn:** Diffusion có thể tạo ra **chi tiết bịa** — tức chi tiết nhìn hợp lý nhưng không tồn tại hoặc không khớp với các ảnh đầu vào.

### Giải pháp cốt lõi

* **HAD không cố làm diffusion hết bịa hoàn toàn.**
* Thay vào đó, HAD học một mạng để dự đoán **điểm bịa ảnh** cho từng pixel.
* Pixel nào có điểm bịa cao sẽ bị loại khỏi loss khi train 3DGS.
* Nhờ đó, 3DGS vẫn nhận được lợi ích từ ảnh diffusion, nhưng tránh học theo các pixel sai.

### Ý tưởng một câu

* **HAD = 3DGS + bộ sửa ảnh diffusion + bộ chấm điểm bịa ảnh.**
* Diffusion tạo ảnh bổ sung.
* Bộ chấm điểm bịa ảnh kiểm tra pixel nào đáng tin.
* 3DGS chỉ học từ phần đáng tin của ảnh bổ sung.

Nguồn chính: paper HAD và project page của tác giả. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

# 2. Bài toán

### Đầu vào

Ta có một tập ảnh đầu vào đã biết camera:

$$
P = \{(I_n, C_n) \mid n \in \{0, \ldots, N\}\}
$$

Trong đó:

* $I_n$: ảnh RGB thứ $n$.
* $C_n$: camera của ảnh thứ $n$.
* $P$: toàn bộ ảnh đầu vào.

### Mục tiêu

* Train một mô hình 3DGS $\Phi$.
* Mô hình này cần render tốt:
  * tại các camera đã có ảnh đầu vào;
  * tại các camera mới chưa thấy trong lúc train.

### Khó khăn

* Khi số ảnh đầu vào ít, scene bị thiếu quan sát.
* 3DGS dễ học sai hình học hoặc thiếu vùng bị che khuất.
* Diffusion có thể sửa ảnh render từ 3DGS, nhưng ảnh diffusion không luôn đúng.
* Nếu dùng toàn bộ ảnh diffusion làm supervision, 3DGS có thể học luôn **chi tiết bịa**.

### Cách HAD đặt lại bài toán

Thay vì hỏi:

* “Làm sao để diffusion không bịa?”

HAD hỏi:

* “Trong ảnh diffusion, pixel nào đáng tin, pixel nào có khả năng là chi tiết bịa?”

Đây là điểm mới chính của paper: HAD biến hallucination thành một bài toán **chấm điểm độ tin cậy theo từng pixel**. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

# 3. Methodology

## 3.1. Bộ thuật ngữ thống nhất

| Thuật ngữ trong paper | Gọi thống nhất trong bài này |
|---|---|
| input views / training views | ảnh đầu vào |
| novel view | ảnh góc nhìn mới |
| augmented novel view | ảnh bổ sung |
| hallucination / aliens | chi tiết bịa |
| hallucination score | điểm bịa ảnh |
| hallucination mask | mặt nạ bỏ pixel sai |
| diffusion prior | bộ sửa ảnh diffusion |
| multi-view encoder | bộ đọc nhiều ảnh |
| 3DGS rendering | ảnh render từ 3DGS |

---

## 3.2. Preliminary: 3D Gaussian Splatting

### Biểu diễn scene

3DGS biểu diễn scene bằng nhiều Gaussian 3D:

$$
\{(\mu_i, S_i, R_i, \delta_i, c_i)\}_{i=1}^{N}
$$

Trong đó:

* $\mu_i$: tâm Gaussian.
* $S_i$: kích thước Gaussian.
* $R_i$: hướng xoay Gaussian.
* $\delta_i$: độ đục học được.
* $c_i$: màu của Gaussian.

### Độ đục của Gaussian

Paper viết:

$$
\alpha_i
=
\delta_i
\exp
\left[
-\frac{1}{2}
(x-\mu_i)^\top
\Sigma_i^{-1}
(x-\mu_i)
\right]
$$

với:

$$
\Sigma_i = R_i S_i S_i^\top R_i^\top
$$

Giải thích:

* $x$ là điểm đang xét.
* $\mu_i$ là tâm Gaussian.
* $x-\mu_i$ đo khoảng cách từ điểm $x$ tới tâm Gaussian.
* $\Sigma_i$ mô tả hình dạng và hướng của Gaussian.
* $\delta_i$ là độ đục tối đa.
* $\alpha_i$ là độ đục thực tế tại điểm $x$.

Trực giác:

* Điểm càng gần tâm Gaussian thì $\alpha_i$ càng lớn.
* Điểm càng xa tâm Gaussian thì $\alpha_i$ càng nhỏ.
* Mỗi Gaussian giống một “đám mây màu” trong không gian 3D.

### Render màu pixel

Paper dùng công thức trộn màu:

$$
C(p)
=
\sum_{i=1}^{N}
c_i \alpha_i
\prod_{j=1}^{i-1}
(1-\alpha_j)
$$

Trong đó:

* $p$: pixel trên ảnh.
* $C(p)$: màu cuối cùng của pixel $p$.
* $c_i$: màu của Gaussian thứ $i$.
* $\alpha_i$: độ đục của Gaussian thứ $i$.
* $\prod_{j=1}^{i-1}(1-\alpha_j)$: phần ánh sáng còn lại sau khi đi qua các Gaussian phía trước.

Ý nghĩa:

* Gaussian phía trước che nhiều thì Gaussian phía sau đóng góp ít.
* Gaussian phía trước trong suốt thì Gaussian phía sau vẫn nhìn thấy được.
* Đây là cách 3DGS render ảnh từ tập Gaussian 3D.

---

## 3.3. Preliminary: bộ sinh ảnh góc nhìn mới trực tiếp

Paper viết:

$$
i_c = FFD(P \mid c)
$$

Trong đó:

* $P$: tập ảnh đầu vào.
* $c$: camera của góc nhìn mới.
* $i_c$: ảnh được sinh ra ở camera $c$.
* $FFD$: mạng sinh ảnh góc nhìn mới trực tiếp.

Ý nghĩa:

* Cho mạng nhiều ảnh đầu vào.
* Hỏi mạng: “Nếu camera ở vị trí $c$, ảnh sẽ trông như thế nào?”
* LVSM là một mô hình thuộc nhóm này.

Trong HAD:

* LVSM không phải module reconstruct chính.
* Tác giả chỉ reuse phần **bộ đọc nhiều ảnh** của LVSM.
* Mục đích là giúp mạng hiểu quan hệ giữa các ảnh đầu vào để kiểm tra ảnh diffusion có bịa hay không. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 3.4. Preliminary: diffusion dùng để sửa ảnh

### Công thức thêm nhiễu

Paper viết:

$$
x_\tau
=
\alpha_\tau x
+
\sigma_\tau \epsilon,
\quad
\epsilon \sim \mathcal{N}(0, I)
$$

Trong đó:

* $x$: ảnh sạch.
* $x_\tau$: ảnh sau khi thêm nhiễu ở bước $\tau$.
* $\epsilon$: nhiễu Gaussian.
* $\alpha_\tau$: lượng ảnh gốc còn giữ lại.
* $\sigma_\tau$: lượng nhiễu được thêm vào.
* $\tau$: bước diffusion.

Trực giác:

* $\tau$ nhỏ: ảnh còn giống ảnh thật.
* $\tau$ lớn: ảnh bị nhiễu nhiều.
* Diffusion học quá trình ngược lại: từ ảnh nhiễu, sửa dần về ảnh sạch.

### Công thức học dự đoán nhiễu

Paper viết:

$$
\mathbb{E}_{x \sim p_{data},\ \tau \sim p_\tau,\ \epsilon \sim \mathcal{N}(0,I)}
\left[
\left\|
\epsilon
-
\epsilon_\theta(x_\tau; c, \tau)
\right\|_2^2
\right]
$$

Trong đó:

* $\epsilon$: nhiễu thật.
* $\epsilon_\theta(\cdot)$: mạng diffusion dự đoán nhiễu.
* $c$: điều kiện đầu vào.
* $x_\tau$: ảnh bị nhiễu.
* $\tau$: bước diffusion.

Trong HAD:

* Diffusion không được dùng để sinh ảnh từ text.
* Diffusion được dùng như **bộ sửa ảnh**.
* Đầu vào là ảnh render lỗi từ 3DGS.
* Đầu ra là ảnh đã được sửa để dùng làm ảnh bổ sung.

---

## 3.5. Loss tổng của HAD

HAD train 3DGS bằng hai nguồn supervision:

$$
\arg \min_{\Phi}
\lambda_{input} L_{input}
+
\lambda_{novel} L_{novel}
$$

Trong đó:

* $\Phi$: tham số của 3DGS.
* $L_{input}$: loss trên ảnh đầu vào thật.
* $L_{novel}$: loss trên ảnh bổ sung.
* $\lambda_{input}$: trọng số cho ảnh đầu vào.
* $\lambda_{novel}$: trọng số cho ảnh bổ sung.

Ý nghĩa:

* Ảnh đầu vào là nguồn đáng tin nhất.
* Ảnh bổ sung giúp tăng số góc nhìn để train.
* Nhưng ảnh bổ sung có thể chứa chi tiết bịa, nên cần kiểm soát bằng mặt nạ.

---

## 3.6. Loss trên ảnh đầu vào

Paper dùng:

$$
L_{input}
=
0.8 L_1(R_\Phi(c), i)
+
0.2 L_{D\text{-}SSIM}(R_\Phi(c), i)
$$

Trong đó:

* $i$: ảnh đầu vào thật.
* $c$: camera của ảnh đó.
* $R_\Phi(c)$: ảnh 3DGS render tại camera $c$.
* $L_1$: sai khác pixel.
* $L_{D\text{-}SSIM}$: sai khác cấu trúc ảnh.

Ý nghĩa:

* Render từ 3DGS tại đúng camera của ảnh thật.
* So sánh render với ảnh thật.
* Đây là loss 3DGS bình thường, chưa phải điểm mới của HAD.

---

## 3.7. Loss trên ảnh bổ sung

HAD tạo tập ảnh bổ sung:

$$
\tilde{P}
=
\{(M_t, \tilde{I}_t, \tilde{C}_t)
\mid
t \in \{0, \ldots, T\}\}
$$

Trong đó:

* $\tilde{I}_t$: ảnh bổ sung.
* $\tilde{C}_t$: camera của ảnh bổ sung.
* $M_t$: mặt nạ bỏ pixel sai.

Loss trên ảnh bổ sung:

$$
L_{novel}
=
L_1
\left(
\neg m \odot R_\Phi(\tilde{c}),
\neg m \odot \tilde{i}
\right)
+
L_{D\text{-}SSIM}
\left(
\neg m \odot R_\Phi(\tilde{c}),
\neg m \odot \tilde{i}
\right)
$$

Trong đó:

* $\tilde{i}$: ảnh bổ sung.
* $\tilde{c}$: camera của ảnh bổ sung.
* $m$: mặt nạ bỏ pixel sai.
* $\neg m$: phần pixel được giữ lại.
* $\odot$: nhân từng pixel.
* $R_\Phi(\tilde{c})$: ảnh 3DGS render tại camera mới.

Cách hiểu:

* Nếu $m[p] = 1$, pixel $p$ bị xem là sai.
* Khi đó $\neg m[p] = 0$, pixel này bị loại khỏi loss.
* Nếu $m[p] = 0$, pixel $p$ được giữ lại.
* Khi đó $\neg m[p] = 1$, pixel này được dùng để train 3DGS.

Đây là công thức quan trọng nhất của HAD:

* HAD không cho 3DGS học toàn bộ ảnh diffusion.
* HAD chỉ cho 3DGS học phần không bị đánh dấu là chi tiết bịa. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 3.8. Bộ sửa ảnh diffusion

HAD reuse diffusion prior từ Difix3D.

Công thức:

$$
\tilde{i}_G
=
G
\left(
R_\Phi(\tilde{c}) \mid i_{ref}
\right)
$$

Trong đó:

* $R_\Phi(\tilde{c})$: ảnh render từ 3DGS ở camera mới.
* $i_{ref}$: ảnh đầu vào được chọn làm ảnh tham chiếu.
* $G$: bộ sửa ảnh diffusion.
* $\tilde{i}_G$: ảnh diffusion đã sửa.

Quy trình:

* 3DGS render một ảnh ở góc nhìn mới.
* Ảnh này có thể bị lỗi vì số ảnh đầu vào ít.
* Bộ sửa ảnh diffusion nhận ảnh render lỗi và một ảnh tham chiếu.
* Nó sinh ra ảnh đã sửa.
* Nhưng ảnh đã sửa có thể chứa chi tiết bịa. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 3.9. Bộ chấm điểm bịa ảnh

HAD học một mạng chấm điểm bịa ảnh:

$$
s
=
S_\theta
\left(
\tilde{i}_G
\mid
R_\Phi(\tilde{c}),
F_{\tilde{c}}
\right)
$$

Trong đó:

* $s$: điểm bịa ảnh theo từng pixel.
* $S_\theta$: mạng chấm điểm bịa ảnh.
* $\tilde{i}_G$: ảnh diffusion đã sửa.
* $R_\Phi(\tilde{c})$: ảnh render gốc từ 3DGS.
* $F_{\tilde{c}}$: đặc trưng nhiều ảnh tại camera mới.

Ý nghĩa:

* Mạng nhìn ảnh diffusion đã sửa.
* Mạng nhìn thêm ảnh render gốc từ 3DGS.
* Mạng dùng thông tin từ nhiều ảnh đầu vào.
* Sau đó mạng dự đoán pixel nào có khả năng là chi tiết bịa.

Kiến trúc gồm:

* **Bộ đọc nhiều ảnh:** reuse từ LVSM, giữ cố định khi train.
* **Nhánh chấm điểm:** U-Net nhỏ 3 lớp, được train để dự đoán điểm bịa ảnh.

Paper cho biết bộ chấm điểm này dùng pretrained LVSM encoder và một U-Net 3 lớp để dự đoán bản đồ điểm bịa ảnh. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 3.10. Bộ đọc nhiều ảnh

Paper viết:

$$
F_{\tilde{c}}
=
V(P \mid \tilde{c})
$$

Trong đó:

* $P$: tập ảnh đầu vào.
* $\tilde{c}$: camera mới.
* $V$: bộ đọc nhiều ảnh.
* $F_{\tilde{c}}$: đặc trưng nhiều ảnh tại camera mới.

Ý nghĩa:

* Bộ đọc nhiều ảnh nhìn các ảnh đầu vào.
* Nó gom thông tin cần thiết cho camera mới.
* Thông tin này giúp mạng biết ảnh diffusion có khớp với scene thật hay không.

Vì sao cần bước này?

* Nếu chỉ nhìn ảnh diffusion, rất khó biết chi tiết nào là thật hay bịa.
* Cần so sánh với nhiều ảnh đầu vào.
* LVSM đã học cách đọc nhiều ảnh, nên HAD reuse phần này.

---

## 3.11. Cách train bộ chấm điểm bịa ảnh

HAD không cần gán nhãn thủ công.

Với mỗi camera mới, tác giả tạo bộ ba ảnh:

* $I^{gt}$: ảnh thật ở camera đó.
* $R_\Phi(\tilde{c})$: ảnh render từ 3DGS.
* $\tilde{i}_G$: ảnh diffusion đã sửa.

Điểm bịa ảnh ground-truth được tạo bằng MAE:

$$
s^{gt}
=
\text{MAE}(\tilde{i}_G, I^{gt})
$$

Sau đó train mạng bằng L2 loss:

$$
L_{score}
=
\|s - s^{gt}\|_2^2
$$

Ý nghĩa:

* Nếu ảnh diffusion khác ảnh thật nhiều ở pixel nào, pixel đó có điểm bịa cao.
* Nếu ảnh diffusion gần ảnh thật, pixel đó có điểm bịa thấp.
* Cách này biến lỗi diffusion thành nhãn huấn luyện mà không cần annotate thủ công.

Paper mô tả bộ dữ liệu train bằng pipeline Difix3D: mỗi scene dùng 9 ảnh đầu vào để train 3DGS, sau đó tạo 100 ảnh bổ sung ở resolution $960 \times 540$; ground-truth ảnh thật ở camera tương ứng được dùng để tính điểm bịa ảnh. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 3.12. Multi-sampling: tạo nhiều ảnh rồi chọn pixel ít bịa nhất

Một ảnh tham chiếu có thể không đủ thông tin cho mọi vùng.

HAD làm như sau:

* Chọn nhiều ảnh đầu vào làm ảnh tham chiếu.
* Với mỗi ảnh tham chiếu, diffusion tạo một ảnh bổ sung.
* Mỗi ảnh bổ sung có một bản đồ điểm bịa ảnh.
* Với từng pixel, chọn phiên bản có điểm bịa thấp nhất.

Công thức:

$$
\{(\tilde{i}^{k}_{G}, s^k) \mid k \in \{1,\ldots,K\}\}
$$

Sau đó:

$$
\tilde{i}[p]
=
\tilde{i}^{k^*}_{G}[p],
\quad
k^*
=
\arg\min_k s^k[p]
$$

Trong đó:

* $k$: chỉ số ảnh tham chiếu.
* $\tilde{i}^{k}_{G}$: ảnh diffusion từ ảnh tham chiếu thứ $k$.
* $s^k$: điểm bịa ảnh tương ứng.
* $p$: pixel đang xét.
* $k^*$: phiên bản có điểm bịa thấp nhất tại pixel $p$.

Ý nghĩa:

* Với mỗi pixel, nhiều ảnh diffusion cùng “tranh cử”.
* HAD chọn pixel từ ảnh có điểm bịa thấp nhất.
* Cách này tận dụng nhiều ảnh đầu vào hơn mà không cần train lại diffusion.

Paper cho thấy ArgMin, tức chọn pixel có điểm bịa thấp nhất, tốt hơn weighted average trong ablation. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 3.13. Toàn bộ pipeline

```text
Input:
  P = tập ảnh đầu vào có camera

Train 3DGS:
  1. Lấy ảnh đầu vào i và camera c.
  2. Render ảnh từ 3DGS:
       RΦ(c)
  3. Tính loss ảnh đầu vào:
       Linput

Tạo ảnh bổ sung:
  4. Chọn camera mới c~
  5. Render ảnh từ 3DGS:
       RΦ(c~)
  6. Dùng diffusion sửa ảnh:
       i~G = G(RΦ(c~) | iref)
  7. Dùng bộ đọc nhiều ảnh:
       Fc~ = V(P | c~)
  8. Dùng mạng chấm điểm:
       s = Sθ(i~G | RΦ(c~), Fc~)
  9. Threshold s để tạo mặt nạ m
  10. Tính loss ảnh bổ sung:
       chỉ dùng pixel không bị đánh dấu là sai

Update:
  11. Tối ưu 3DGS bằng:
       λinput Linput + λnovel Lnovel
```

---

## 3.14. HAD reuse những gì?

| Thành phần reuse | Vai trò trong HAD |
|---|---|
| 3DGS | Biểu diễn scene và render ảnh |
| Difix3D | Bộ sửa ảnh diffusion |
| LVSM | Bộ đọc nhiều ảnh cho mạng chấm điểm bịa ảnh |
| U-Net nhỏ | Nhánh dự đoán điểm bịa ảnh |
| Ý tưởng masked supervision | Chỉ train bằng pixel đáng tin |

Điểm mới không nằm ở việc tạo diffusion model mới.

Điểm mới nằm ở:

* học điểm bịa ảnh theo từng pixel;
* dùng điểm đó để mask ảnh bổ sung;
* dùng điểm đó để chọn pixel tốt nhất từ nhiều ảnh diffusion;
* cho 3DGS học từ ảnh diffusion theo cách an toàn hơn.

---

# 4. Kết quả

## 4.1. DL3DV, setting 9 ảnh đầu vào

| Method | PSNR | SSIM | LPIPS |
|---|---:|---:|---:|
| Gsplat-3DGS | 19.004 | 0.679 | 0.281 |
| Gsplat-MCMC | 20.532 | 0.721 | 0.225 |
| Difix3D | 21.355 | 0.734 | 0.199 |
| HAD, full model | **22.134** | **0.757** | **0.190** |

Nhận xét:

* HAD cao hơn Difix3D khoảng **+0.78 dB PSNR** trên DL3DV.
* SSIM cũng tăng từ 0.734 lên 0.757.
* LPIPS giảm từ 0.199 xuống 0.190.
* Điều này cho thấy HAD không chỉ làm ảnh nhìn tốt hơn, mà còn giữ ảnh gần ground-truth hơn. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 4.2. MipNeRF360, cross-domain

| Method | PSNR | SSIM | LPIPS |
|---|---:|---:|---:|
| Gsplat-3DGS | 15.748 | 0.424 | 0.431 |
| Gsplat-MCMC | 17.102 | 0.454 | 0.385 |
| FSGS | 17.940 | 0.492 | 0.468 |
| GenFusion | 18.360 | 0.496 | 0.465 |
| Difix3D | 18.001 | 0.475 | 0.350 |
| HAD | **18.689** | **0.5094** | **0.334** |

Nhận xét:

* HAD vẫn tốt khi chuyển sang dataset khác.
* HAD cao hơn Difix3D khoảng **+0.69 dB PSNR** trên MipNeRF360.
* Kết quả này cho thấy bộ chấm điểm bịa ảnh không chỉ hoạt động trên dataset train. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 4.3. Ablation: từng thành phần có tác dụng gì?

| Variant | PSNR | SSIM | LPIPS |
|---|---:|---:|---:|
| Difix3D | 21.355 | 0.734 | 0.199 |
| Difix3D + HAD | 21.779 | 0.749 | 0.195 |
| Difix3D + HAD + Multi-sampling | 21.983 | 0.755 | 0.195 |
| HAD full model | **22.134** | **0.757** | **0.190** |

Kết luận:

* Thêm bộ chấm điểm bịa ảnh đã cải thiện rõ.
* Multi-sampling tiếp tục cải thiện.
* Full model đạt kết quả tốt nhất. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

## 4.4. Ablation: bộ chấm điểm bịa ảnh

| Estimator | MAE ↓ |
|---|---:|
| Retrained Difix3D | 0.058 |
| HAD không dùng bộ đọc nhiều ảnh pretrained | 0.054 |
| HAD full | **0.043** |

Kết luận:

* Bộ đọc nhiều ảnh từ LVSM rất quan trọng.
* Nếu không có bộ đọc nhiều ảnh tốt, mạng khó phát hiện pixel nào là chi tiết bịa.
* Diffusion tự chấm điểm không tốt bằng cách dùng bộ đọc nhiều ảnh riêng. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

# 5. Hạn chế

### 5.1. Điểm bịa ảnh được học từ MAE

* Ground-truth điểm bịa ảnh được tính bằng sai khác giữa ảnh diffusion và ảnh thật.
* Nhưng MAE không chỉ đo chi tiết bịa.
* MAE cũng có thể tăng do:
  * lệch màu;
  * lệch sáng;
  * sai căn chỉnh nhỏ;
  * khác biệt texture không quan trọng.

### 5.2. Mặt nạ là threshold cứng

* Pixel bị chia thành hai loại:
  * dùng;
  * bỏ.
* Cách này đơn giản và hiệu quả.
* Nhưng nó chưa tận dụng được mức độ tin cậy liên tục.
* Một hướng cải tiến là dùng uncertainty hoặc EDL để biến mặt nạ thành trọng số mềm.

### 5.3. Method mới dừng ở pixel-level

* HAD kiểm soát loss ở từng pixel.
* Nhưng chưa trực tiếp kiểm soát Gaussian nào gây lỗi.
* Một hướng phát triển là chuyển điểm bịa ảnh từ pixel-level sang Gaussian-level để:
  * giảm opacity;
  * dừng densify;
  * prune Gaussian;
  * hoặc sửa cấu trúc 3DGS.

### 5.4. Phụ thuộc LVSM

* HAD reuse bộ đọc nhiều ảnh từ LVSM.
* Nếu bộ đọc nhiều ảnh không đủ tốt, điểm bịa ảnh cũng bị ảnh hưởng.
* Paper cũng nêu rằng method bị giới hạn bởi pretrained multi-view encoder và chủ yếu được kiểm chứng trên vùng đã được quan sát. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

### 5.5. Chi phí train scorer không nhỏ

* Tác giả train bộ chấm điểm bịa ảnh trong 10k iterations.
* Batch size là 2/GPU.
* Chi phí khoảng 28 giờ trên 8 GPU NVIDIA V100 32GB. ([arxiv.org](https://arxiv.org/html/2605.16873v1))

---

# Kết luận ngắn

* HAD là một hướng rất hợp lý cho sparse-view 3D reconstruction.
* Nó không thay diffusion, không thay 3DGS, mà thêm một lớp kiểm tra giữa diffusion và 3DGS.
* Điểm mạnh nhất là biến lỗi “diffusion bịa” thành một bản đồ điểm bịa ảnh theo từng pixel.
* Nhờ đó, 3DGS chỉ học từ phần đáng tin của ảnh diffusion.
* Novelty chính của paper nằm ở **hallucination-aware supervision**: ảnh bổ sung từ diffusion không còn là teacher tuyệt đối, mà là teacher cần được kiểm tra trước khi dùng.
  