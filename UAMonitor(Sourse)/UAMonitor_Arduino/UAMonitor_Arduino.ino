#define Flu A2
#define OD A1
#define ledFlu 9
#define ledOD 10



void setup() {
  
  Serial.begin(9600);
  delay(30);
  pinMode(ledFlu, OUTPUT);
  pinMode(ledOD, OUTPUT);
  digitalWrite(ledFlu,0);
  digitalWrite(ledOD,0);
}

int vFlu=0,vOD=0,pos, i=0,res;
String dat,dat1,dat2;

void loop() {
  int vFlu1 = analogRead(Flu);
  int vOD1 = analogRead(OD);
  vFlu1 = map(vFlu1, 0, 1024, 0, 200);
  vOD1 = map(vOD1, 0, 1024, 0, 200);
  Serial.println(String(vFlu1) + "," + String(vOD1));
  if(Serial.available()){
    dat = Serial.readString(); 
    pos = dat.indexOf(',');
    dat1= dat.substring(0,pos);
    dat2= dat.substring(pos+1); 

    if(vFlu != dat1.toInt()){
      vFlu = dat1.toInt();  
      digitalWrite(ledFlu,vFlu); 
    }
    if(vOD != dat2.toInt()){
      vOD = dat2.toInt();  
      digitalWrite(ledOD,vOD);
    }
    if(dat2.toInt()==1 && dat1.toInt() == 1){
      i = 0;
    }
    if(vOD == 1 && vOD == 1){
      res = 200%i;
      if(res < 100){
        digitalWrite(ledFlu,1);
        digitalWrite(ledOD,0);
        }
      else{
        digitalWrite(ledFlu,0);
        digitalWrite(ledOD,1);  
        }
    }     
  delay(10);
  } 
}
