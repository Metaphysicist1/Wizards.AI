sudo apt install git virtualenv

git clone https://github.com/Metaphysicist1/Wizards.AI.git

function act(){
	virtualenv .speech

	source .speech/bin/activate
	cd application
}

act

function other(){
	pip install -r requirements.txt

	sudo apt-get install  python3-all-dev python3-pip build-essential swig  libpulse-dev libasound2-dev

	gdown https://drive.google.com/uc?id=1rMV2hrefpMy7C8ShF4QsNc61J4VzRurn
	unzip daanzu_vosk.zip

	gdown https://drive.google.com/uc?id=1II3B_m-FEniKikCEJrTd_sAURfeDmLGr
	unzip small_vosk.zip

	pip install pocketsphinx==0.1.15
	
	}
other
