import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO

def show_qr_code_generator():
    st.title("QR Code Generator")

    # Fonction pour générer un code QR
    def generate_qr_code(url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

    # Fonction pour convertir une image PIL en bytes
    def get_image_bytes(img):
        buf = BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        return byte_im

    # Entrée URL de l'utilisateur
    url = st.text_input("Enter text to generate QR code:")

    if url:
        # Générer le code QR
        img = generate_qr_code(url)
        
        # Convertir l'image en bytes pour l'affichage et le téléchargement
        img_bytes = get_image_bytes(img)

        # Afficher le code QR
        st.image(img_bytes, caption=url.replace(" ","_"), width=300)

        # Option pour télécharger le code QR
        st.download_button(
            label="Download QR Code",
            data=img_bytes,
            file_name="qr_code.png",
            mime="image/png"
        )

if __name__ == "__main__":
    show_qr_code_generator()

