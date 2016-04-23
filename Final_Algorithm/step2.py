import socket


## Step 2
print socket.gethostbyname('localhost')
my_Address =  socket.gethostbyname('google.com')

print my_Address

hello = my_Address.split('.')[0] + '.' + my_Address.split('.')[1]
print hello
