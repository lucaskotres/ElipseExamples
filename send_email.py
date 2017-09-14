import smtplib
import base64
avg = 100

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("lucaskotres@gmail.com", "Epj!igo169952")

msg = f'Hello! The EPM Processor send a message to you:  the average is {avg}. Hugs!'

msg = "YOUR MESSAGE!"
server.sendmail("lucaskotres@gmail.com", "kotres@elipse.com.br", msg)
server.quit()