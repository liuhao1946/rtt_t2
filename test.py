import pylink


if __name__ == '__main__':
    serial_no = '59768896'
    jk = pylink.JLink()

    # Open a connection to your J-Link.
    jk.open()

    try:
        # nrf52840xxaa
        # stm32f103c8
        jk.connect('stm32f103c8', verbose=True)
    except Exception as e:
        print(e)

    if jk.connected():
        print('@@jk is connect...')
    else:
        print('jk open fail..')

    jk.close()
    print('jk_close')
