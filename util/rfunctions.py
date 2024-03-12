def route_upload(request: Request):
    key = request.headers.get('Content-Type', None)
    if not key:
        return b'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 5\r\n\r\nFatal'

    key = key.split(';')[1].strip().replace('boundary=', '')
    # ends with webkit form boundary, and they're in the middle
    print(key)

    first_bound = f'--{key}--\r\n'.encode()
    final_bound = f'\r\n--{key}--\r\n'.encode()

    data = request.body
    data = data.replace(first_bound, b'', 1)  # adding the one will keep the boundary in the middle, only removing the first one
    data = data.replace(final_bound, b'')

    general_bound = f'\r\n--{key}\r\n'
    data = data.split(general_bound.encode())
    the_data = {}

    for data_point in data:
        data_header = data_point.split(b'\r\n\r\n')[0].decode()
        data_header = data_header.split('name')[1].strip()
        data_value = data_point.split(b'\r\n\r\n')[1]
        if 'image' not in data_header:
            data_value = data_value.decode()
        the_data[data_header] = data_value
        # will need to implement buffering if the data is long
        # if it's big, check if the content length matches the length of the body
        # will need to read again if it doesn't suit the body
    print(data)
    print(the_data)

    return b'HTTP/1.1 200 OK\r\nContent-Type: text/plain'
