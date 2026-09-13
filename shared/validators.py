import os
import struct
import tempfile

from django.core.exceptions import ValidationError

# Límites por defecto
MAX_IMAGE_SIZE_MB = 5
MAX_REEL_SIZE_MB = 50
MAX_REEL_DURATION_SECONDS = 7


def validate_upload_size(upload, max_mb, label='El archivo'):
    try:
        size_mb = upload.size / (1024 * 1024)
    except (AttributeError, TypeError):
        return
    if size_mb > max_mb:
        label = label[:1].upper() + label[1:]
        raise ValidationError(
            f'{label} supera el máximo permitido de {max_mb} MB '
            f'(peso actual: {size_mb:.1f} MB)'
        )


def import_upload_to_temp(upload, suffix='.upload'):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        if hasattr(upload, 'seek'):
            upload.seek(0)
        for chunk in upload.chunks():
            tmp.write(chunk)
        tmp.close()
        return tmp.name
    except Exception:
        tmp.close()
        try:
            os.remove(tmp.name)
        except OSError:
            pass
        return None


def parse_mp4_duration(path):
    """Extrae la duración (segundos) de un MP4/MOV leyendo el atom mvhd.

    Devuelve float o None si no puede determinarse.
    """
    try:
        fsize = os.path.getsize(path)
    except OSError:
        return None
    if fsize <= 0 or fsize > 512 * 1024 * 1024:
        return None

    def _next_box(f, pos, end):
        """Lee un box en pos; devuelve (box_type, start, size) o None."""
        if pos + 8 > end:
            return None
        f.seek(pos)
        header = f.read(8)
        if len(header) < 8:
            return None
        size, btype = struct.unpack('>I4s', header)
        if size == 1:
            large = f.read(8)
            if len(large) < 8:
                return None
            size = struct.unpack('>Q', large)[0]
        elif size == 0:
            size = end - pos
        if size < 8:
            return None
        return btype, pos, size

    with open(path, 'rb') as f:
        end = fsize
        pos = 0
        mvhd_pos = None
        while True:
            box = _next_box(f, pos, end)
            if box is None:
                break
            btype, bpos, bsize = box
            if btype in (b'moov', b'MOVI'):
                child = bpos + 8
                child_end = bpos + bsize
                while True:
                    cbox = _next_box(f, child, child_end)
                    if cbox is None:
                        break
                    ctype, cpos, csize = cbox
                    if ctype == b'mvhd':
                        mvhd_pos = cpos
                        break
                    child = cpos + csize
                break
            pos = bpos + bsize

        if mvhd_pos is None:
            return None

        f.seek(mvhd_pos + 8)
        b = f.read(1)
        if not b:
            return None
        version = struct.unpack('>B', b)[0]
        if version == 1:
            f.seek(mvhd_pos + 28)
            ts = f.read(4)
            dur = f.read(8)
            if len(ts) < 4 or len(dur) < 8:
                return None
            timescale = struct.unpack('>I', ts)[0]
            duration = struct.unpack('>Q', dur)[0]
        else:
            f.seek(mvhd_pos + 20)
            ts = f.read(4)
            dur = f.read(4)
            if len(ts) < 4 or len(dur) < 4:
                return None
            timescale = struct.unpack('>I', ts)[0]
            duration = struct.unpack('>I', dur)[0]
        if not timescale:
            return None
        return duration / timescale


def validate_reel_video(upload):
    raise_error = None
    try:
        validate_upload_size(upload, MAX_REEL_SIZE_MB, 'el video del reel')
    except ValidationError as exc:
        raise_error = exc

    tmp_path = import_upload_to_temp(upload, suffix='.mp4')
    seconds = None
    if tmp_path:
        try:
            seconds = parse_mp4_duration(tmp_path)
        except Exception:
            seconds = None
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    if raise_error is not None:
        raise raise_error

    if seconds is None:
        raise ValidationError(
            'No se pudo verificar la duración: sube un video MP4 válido '
            f'(máximo {MAX_REEL_DURATION_SECONDS} segundos)'
        )
    if seconds > MAX_REEL_DURATION_SECONDS:
        raise ValidationError(
            f'El video supera los {MAX_REEL_DURATION_SECONDS} segundos permitidos '
            f'(duración detectada: {seconds:.0f}s)'
        )
    return upload