import time
import board
import busio
import adafruit_fingerprint
import serial
import logging

class FingerPrintControl:

    def __init__(self,log_path):
        super().__init__()

        # Instanciando classe com configurações do Sensor
        self._uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
        self._finger = adafruit_fingerprint.Adafruit_Fingerprint(self._uart)

        # Setando arquivo de Log
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        self._logger = logging.getLogger(__name__)

    def read_fingerprint(self):

        finger = self._finger
        logger = self._logger

        print("Waiting for image...")
        # Aguardando leitura da digital
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        # Leitura realizada e transformando para imagem
        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False
        # Buscando na memória do dispositivo
        if finger.finger_search() != adafruit_fingerprint.OK:
            return False
        # Incrementando log
        logger.info(f"- ID encontrado: {finger.finger_id}")
        return finger.finger_id

    def register_fingerprint(self, memory_position):

        """Lê duas vezes a digital para registrar na memória do dispositivo (memory_position)"""
        finger = self._finger
        logger = self._logger

        # Inicia loop de leitura
        for fingerimg in range(1, 3):
            # Posiciona pela primeira vez
            if fingerimg == 1:
                print("Posicione o dedo no sensor...", end="", flush=True)
                logger.info(f"- Cadastrando digital na posição {memory_position}")
            else:
                print("Posicione o mesmo dedo no sensor...", end="", flush=True)
                logger.info(f"- Repetindo a leitura da digital na posição {memory_position} para cadastro")

            while True:
                i = finger.get_image()
                if i == adafruit_fingerprint.OK:
                    logger.info("- Imagem da digital capturada")
                    print("Imagem capturada")
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    print(".", end="", flush=True)
                    None
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    print("Erro na leitura")
                    logger.error("- Erro no cadastro da digital")
                    return False
                else:
                    logger.error("- Erro desconhecido")
                    return False

            print("Armazenando imagem...", end="", flush=True)
            i = finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                print("Imagem validada e guardada")
                logger.info("- Imagem da digital registrada na memória")
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    print("Digital muito embaçada")
                    logger.error("- Digital embaçada")
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    print("Digital não passível de identificar")
                    logger.error("- Digital não passível de identificar")
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    logger.error("- Digital não passível de identificar")
                    print("Digital inválida")
                else:
                    logger.error("- Erro desconhecido")
                return False

            if fingerimg == 1:
                print("Retire o dedo")
                time.sleep(1)
                while i != adafruit_fingerprint.NOFINGER:
                    i = finger.get_image()


        print("Criando modelo...", end="", flush=True)
        i = finger.create_model()
        if i == adafruit_fingerprint.OK:
            logger.info("- Modelo criado")
            print("Modelo criado")
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                logger.info("- Digitais não coincidentes")
                print("Digitais não coincidentes")
            else:
                logger.error("- Erro desconhecido")
            return False

        print("Salvando modelo na posição #%d..." % memory_position, end="", flush=True)
        logger.info("- Salvando modelo na posição #%d..." % memory_position)
        i = finger.store_model(memory_position)
        if i == adafruit_fingerprint.OK:
            print("Salvo")
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                print("Problemas na armazenagem")
                logger.error("- Problemas na armazenagem")
            elif i == adafruit_fingerprint.FLASHERR:
                print("Flash storage error")
                logger.error("- Problemas na hora do flash para armazenagem")
            else:
                print("Other error")
                logger.error("- Erro desconhecido")
            return False

        return True

    def delete_fingerprint(self, memory_position):
        finger = self._finger
        logger = self._logger

        if finger.delete_model(memory_position) == adafruit_fingerprint.OK:
            print(f"A digital {memory_position} foi excluída da memória")
            logger.warning(f"- A digital {memory_position} foi excluída da memória")
        else:
            print("Falha ao deletar da memória")
            logger.error(f"- A digital {memory_position} não foi excluída da memória, pois houve falha")

    def delete_all_fingerprint(self):
        finger = self._finger
        logger = self._logger

        for memory_position in range(127):
            if finger.delete_model(memory_position) == adafruit_fingerprint.OK:
                None
                #print(f"A digital {memory_position} foi excluída da memória")
            else:
                print(f"Falha ao deletar da memória na posição {memory_position}")

        logger.info("- Todas as digitais foram excluídas")

    def getting_memory_allocated(self):
        finger = self._finger
        logger = self._logger

        if finger.read_templates() != adafruit_fingerprint.OK:
            logger.error("- Falha ao ler o sensor e sua memória")
            raise RuntimeError("Falha ao ler o sensor e sua memória")

        logger.info(f"- Posições ocupadas na memória {finger.templates}")

        #print("Fingerprint templates:", finger.templates)
        return finger.templates