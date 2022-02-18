from fingerprint_lib_2 import FingerPrintControl

def main():
    fpg = FingerPrintControl(log_path="../logs/fingerprint.log")
    fpg.delete_all_fingerprint()

if __name__ == '__main__':
	main()
