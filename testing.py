import bencode
import hashlib
import struct
import requests
import socket
import sys
import random


with open('C:/Users/apars/OneDrive/Documents/python/Torrent_client/kali-linux-2024.2-installer-amd64.iso.torrent', 'rb') as f:
    # with open('sample.torrent', 'rb') as f:
    meta_info = f.read()
    torrent_data = bencode.bdecode(meta_info)

announce_url = torrent_data['announce']
# print(announce_url)
index = 0
begin = 0
piece_length = torrent_data['info']['piece length']
total_length = torrent_data['info']['length']
remaining_length = total_length
total_pieces = total_length//piece_length
piece_hash = torrent_data['info']['pieces']
length_downloaded = 0


peer_id = '-PC0001-' + ''.join(str(random.randint(0, 9)) for _ in range(12))
peer_id = str.encode(peer_id)
info_hash = hashlib.sha1(bencode.bencode(torrent_data['info'])).digest()
peers = []
port = 6881

params = {
    'info_hash': info_hash,
    'peer_id': peer_id,
    'port': port,
    'uploaded': 0,
    'downloaded': 0,
    'left': 0,
    'compact': 1,
    'event': 'started'
}

# def print_progress_bar(completed, total, bar_length=40):
#     percent = float(completed) / total
#     arrow = '=' * int(round(percent * bar_length) - 1) + '>'
#     spaces = ' ' * (bar_length - len(arrow))
#     sys.stdout.write(f"\rProgress: [{arrow}{spaces}] {int(round(percent * 100))}%")
#     sys.stdout.flush()


def parse_tracker_response(response_data):
    peers = []
    response = bencode.bdecode(response_data)
    peer_data = response['peers']
    for i in range(0, len(peer_data), 6):
        ip = '.'.join(str(byte) for byte in peer_data[i:i + 4])
        port = struct.unpack('!H', peer_data[i + 4:i + 6])[0]
        peers.append((ip, port))
    return peers


response = requests.get(announce_url, params=params)
response_data = response.content
peers = parse_tracker_response(response_data)
# print(peers)


for ip, port in peers:
    try:
        with socket.create_connection((ip, port)) as sock:
            # Send BitTorrent handshake
            pstrlen = bytes(chr(19).encode('utf-8'))
            pstr = b'BitTorrent protocol'
            reserved = b'\x00' * 8
            # peer_id = b'-PC0003-123456789012'
            handshake = pstrlen + pstr + reserved + info_hash + peer_id
            sock.sendall(handshake)

            # Receive handshake response
            response = sock.recv(68)
            print(f'Connected to {ip}:{port} - {response}')

            # Verify the handshake
            # ????????????????????????

            # Send interested field
            interested_msg = struct.pack('>I', 1) + b'\x02'
            sock.sendall(interested_msg)
            while True:
                # Here sock.recv(4) returns a singleton tuple
                message_len = struct.unpack('>I', sock.recv(4))[0]
                if message_len == 0:
                    # Keep-alive message => ignore
                    continue
                message_id = sock.recv(1)
                payload = sock.recv(message_len - 1)

                if message_id == b'\x04':  # have message
                    piece_index = struct.unpack('>I', payload)[0]
                    print(f'Peer has piece {piece_index}')

                elif message_id == b'\x05':  # bitfield message
                    bitfield = payload
                    print(f'Peer bitfield: {bitfield}')
                    # request_msg = struct.pack(
                    #     '>I', 13) + b'\x06' + struct.pack('>III', index, begin, 32768)
                    # print(f'requested piece no: {index} offset: {begin}')

                elif message_id == b'\x01':  # unchoke message
                    print('Peer unchoked us, we can request pieces')
                    # Example: Request piece 0, block 0, 16384 bytes
                    request_msg = struct.pack(
                        '>I', 13) + b'\x06' + struct.pack('>III', index, begin, 32768)
                    sock.sendall(request_msg)
                    print(f'requested piece no: {index} begin: {begin}')

                elif message_id == b'\x07':  # piece message
                    print('got a piece message')
                    with open(f'raw_binary_file.bin', 'ab') as f:
                        while True:
                            index, begin = struct.unpack('>II', payload[:8])
                            block = payload[8:]
                            print(
                                f'Received piece {index}, block starting at {begin}')

                            # f.seek(begin) # We are sequentially requesting and writing the file so we're good atm
                            f.write(block)

                            length_downloaded = + 32768
                            index = length_downloaded // piece_length
                            begin = (length_downloaded+1) % piece_length
                            remaining_length = total_length - length_downloaded
                            # print_progress_bar(length_downloaded, total_length)

                            if (remaining_length <= 32768):
                                request_msg = struct.pack(
                                    '>I', 13) + b'\x06' + struct.pack('>III', index, begin, remaining_length)

                            # Grabbing the peer and requesting another batch of data from the same peer
                            request_msg = struct.pack(
                                '>I', 13) + b'\x06' + struct.pack('>III', index, begin, 32768)

    except Exception as e:
        print(f'Failed to connect to {ip}:{port} - {e}')

# def start(self):
#         # self.peers = self.get_peers_from_tracker()
#         # print(f'Found peers: {self.peers}')


# for ip, port in peers:
#     connect_to_peer(ip, port)
#     # print(ip, port)
