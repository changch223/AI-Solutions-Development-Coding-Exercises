# 🧪 Malaria Cell Image Classifier (ViT + CNN + VGG16)

This Streamlit web app classifies red blood cell images as either **Parasitized** (infected with malaria) or **Uninfected** using five models:
- Vision Transformer (ViT) — full fine-tuning
- Vision Transformer (ViT) — head-only fine-tuning
- CNN (trained from scratch)
- VGG16 (transfer learning)

---

## 🚀 Live Demo

> Launch this app locally using Streamlit to get instant predictions on microscopy images.

---

## 🧠 Models Used

| Model Type     | Architecture                 | Input Size | Fine-tuning           |
|----------------|------------------------------|------------|------------------------|
| ViT            | `vit_tiny_patch16_224.augreg_in21k` | 224x224    | Full fine-tuned        |
| ViT            | Same as above                | 224x224    | Head-only fine-tuned   |
| CNN            | Custom CNN from scratch      | 224x224    | Fully trained          |
| VGG16          | Keras Transfer Learning      | 130x130    | Top-layer fine-tuned   |

---

## 🖼️ How It Works

1. Upload an image (JPG, PNG).
2. The app processes the image using transforms suited to each model.
3. Each model returns:
   - Predicted label: **Parasitized** or **Uninfected**
   - Confidence score (visualized via progress bar)

---

## 🛠️ Technologies

- [Streamlit](https://streamlit.io/)
- [PyTorch](https://pytorch.org/)
- [TIMM](https://github.com/huggingface/pytorch-image-models)
- [TensorFlow / Keras](https://www.tensorflow.org/)
- [PIL / NumPy](https://python-pillow.org/)

---

## 💻 Installation

```bash
# Clone the repo
git clone https://github.com/your-username/Malaria_Cell_Images-_Dataset_group7.git
cd Malaria_Cell_Images-_Dataset_group7

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

### 📊 Dataset

**Source:** [Kaggle - Cell Images for Malaria Detection](https://www.kaggle.com/datasets/iarunava/cell-images-for-detecting-malaria)

- ~27,558 labeled images
- 2 classes: `Parasitized` and `Uninfected`
- Images were preprocessed to 224x224 resolution
- Normalized to ImageNet stats (mean: `[0.485, 0.456, 0.406]`, std: `[0.229, 0.224, 0.225]`)

---

### 🧠 Models Used

#### 🧩 Vision Transformers (ViT)
- **Architecture:** `vit_tiny_patch16_224.augreg_in21k` from Hugging Face's `timm` library
- **Model 1:** Full fine-tuning (5.5M trainable params)
- **Model 2:** Head-only fine-tuning (386 trainable params)

#### 🧠 VGG16 (
- Transfer learning with added dense layers and dropout
- Achieved ~93% accuracy over 20 epochs

#### 🧠 CNN from Scratch
- Manually designed architecture 
- Used for performance comparison

---

### 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Malaria_Cell_Images-_Dataset_group7.git
cd Malaria_Cell_Images-_Dataset_group7

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # For macOS/Linux
# .\venv\Scripts\activate   # For Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run streamlit_app.py


File Structure:

Malaria_Cell_Images-_Dataset_group7/
│
├── .devcontainer/                   # VS Code container settings
|── .streamlit/config.toml            
├── venv/                           # (virtual env, excluded from Git)
├── .gitignore
├── best_model.h5                   # CNN Keras model
├── best_vgg16_model.h5             # VGG16 transfer learning model
├── first_model.ipynb               # Notebook for training CNN
├── malaria_cells_img_VGG16.ipynb   # VGG training + transfer learning
├── streamlit_app.py                # ✅ Main Streamlit app
├── README.md                       # 📘 This file
├── requirements.txt                # Python dependencies
├── vit_malaria_full.pth            # Fully fine-tuned ViT model
├── vit_head-only-training_malaria.pth # ViT with head-only training
├── vit_malaria.pth                 # ViT original head model
├── ViT_Fine_tuning_with_transfer...ipynb # Optional ViT training notebook



👥 Authors (Group 7)
Abdul-Rasaq Omisesan 
Bikash Giri 
Gavriel Kirichenko 
Chia-Wei Chang 
Callum Arul 
Friba Hussainyar 
Diparshan Bhattarai 

🔗 References

Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner, T., Dehghani, M., Minderer, M., Heigold, G., Gelly, S., Uszkoreit, J., & Houlsby, N. (2020, October 22). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. arXiv.org. https://arxiv.org/abs/2010.11929

Huggingface. (n.d.). GitHub - huggingface/pytorch-image-models: The largest collection of PyTorch image encoders / backbones. Including train, eval, inference, export scripts, and pretrained weights -- ResNet, ResNeXT, EfficientNet, NFNet, Vision Transformer (ViT), MobileNetV4, MobileNet-V3 & V2, RegNet, DPN, CSPNet, Swin Transformer, MaxViT, CoAtNet, ConvNeXt, and more. GitHub. https://github.com/huggingface/pytorch-image-models

Malaria cell Images Dataset. (2018, December 5). Kaggle. https://www.kaggle.com/datasets/iarunava/cell-images-for-detecting-malaria


📄 License

 free for academic, educational, and personal use.