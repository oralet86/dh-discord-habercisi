# Donanimhaber Discord Habercisi

Bu bot, belirtilmiş DonanimHaber forumlarında yeni bir gönderi algıladığında seçilmiş bir Discord kanalına mesaj gönderir.
# Başlarken

    Depoyu yerel makinenize klonlayın.
    Pip install -r requirements.txt ile bağımlılıkları yükleyin.
    Bir Discord botu oluşturun ve sunucunuza ekleyin.
    Botun token'ını kopyalayın ve '.env' içindeki TOKEN değişkenine yapıştırın.
    Botu python 'main.py' ile çalıştırın.

# Kullanım

Bot başlatıldığında otomatik olarak belirtilen donanimhaber forumlarını yeni gönderiler için izlemeye başlayacaktır. Yeni bir gönderi tespit ettiğinde, belirttiğiniz Discord kanalına bir mesaj gönderecektir. Mesajda gönderinin başlığı, yazarın adı, yazarın avatarı (mümkünse), gönderinin içeriği (gönderi içeriği 512 karakterden uzunsa, bot otomatik olarak kısaltacaktır) ve sırasıyla mobile.donanimhaber.com ve forum.donanimhaber.com'da gönderiye yönlendiren iki bağlantı yer alacaktır.

# Konfigürasyon

Botun ön eki varsayılan olarak 'dh'dir, bunu 'main.py' içindeki PREFIX değişkenini düzenleyerek değiştirebilirsiniz. Botu kullanmak için aşağıdaki komutları kullanabilirsiniz:

    ekle 'link': Bağlantısı verilen forumu discord kanalları izleme listesine ekler, bu forumdaki herhangi bir yeni gönderi o kanala gönderilecektir.
    cikar 'link' (İsteğe bağlı): Bağlantısı verilen forumu discord kanalları izleme listesinden kaldırır. Herhangi bir bağlantı verilmezse, eklenen tüm forumlar kaldırılır.   

# Sorun Giderme

Botla ilgili herhangi bir sorun yaşarsanız, lütfen GitHub deposunda bir sorun açın.
