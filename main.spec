# -*- mode: python -*-

block_cipher = None

SETUP_DIR = 'F:\\gitee\\knowledge\\new_yysscript\\'

a = Analysis(['src\\main.py',
              'src/ui/main_widget.py',
              'src/mainwin.py',
              'src/screenshot.py',
              'src/autogui/win_gui.py',
              'src/autogui/autogui.py',
              'src/tools/licence.py',
              'src/screenshot/images.py',
              'src/auto_yuhun.py',
              'src/auto_chapter28.py',
              'src/auto_yuling.py',
              'src/auto_break.py',
              ],
             pathex=['F:\\gitee\\knowledge\\new_yysscript'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='new_tools',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
