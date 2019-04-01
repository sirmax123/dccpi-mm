// based on dccpi project

#include <Python.h>
#include <wiringPi.h>
//This one is not exposed
extern void delayMicrosecondsHard (unsigned int howLong);

// pin numbering follows wiringPi notation
const int dataPin = 0;
const int brakePin = 2;

// see pinout table
//
const int input1Pin = 3;
const int input2Pin = 4;
const int enablePin = 5;


static PyObject * dcc_rpi_encoder_c_send_bit_array(PyObject *self, PyObject *args){
    char const *bit_array;
    char const *bit_array_pos;
    const int count;
    const unsigned int bit_one_part_duration;
    const unsigned int bit_zero_part_duration;
    const unsigned int packet_separation;
    int i;

    if (!PyArg_ParseTuple(args, "siIII", &bit_array, &count,
                          &bit_one_part_duration,
                          &bit_zero_part_duration,
                          &packet_separation))
        return NULL;

    for (i = 0; i < count; i++){
        bit_array_pos = bit_array;
        while (*bit_array_pos){ //string will be null terminated
            if (*bit_array_pos == '0'){
                //Encode 0 with 100us for each part
                digitalWrite(enablePin, LOW);
                digitalWrite(input1Pin, LOW);
                digitalWrite(input2Pin, LOW);
                digitalWrite(input2Pin, HIGH);
                digitalWrite(enablePin, HIGH);
                delayMicrosecondsHard(bit_zero_part_duration);
                digitalWrite(enablePin, LOW);
                digitalWrite(input1Pin, LOW);
                digitalWrite(input2Pin, LOW);
                digitalWrite(input1Pin, HIGH);
                digitalWrite(input2Pin, LOW);
                digitalWrite(enablePin, HIGH);
                delayMicrosecondsHard(bit_zero_part_duration);
            }
            else if (*bit_array_pos == '1'){
                //Encode 1 with 58us for each part
                digitalWrite(enablePin, LOW);
                digitalWrite(input1Pin, LOW);
                digitalWrite(input2Pin, HIGH);
                digitalWrite(enablePin, HIGH);
                delayMicrosecondsHard(bit_one_part_duration);
                digitalWrite(enablePin, LOW);
                digitalWrite(input1Pin, HIGH);
                digitalWrite(input2Pin, LOW);
                digitalWrite(enablePin, HIGH);
                delayMicrosecondsHard(bit_one_part_duration);

            } else {
                // Interpret this case as packet end char.
                // Standard says we should wait 5ms at least
                // and 30ms max between packets.
                digitalWrite(enablePin, LOW);
                digitalWrite(input1Pin, LOW);
                digitalWrite(input2Pin, HIGH);
                digitalWrite(enablePin, HIGH);
                delay(packet_separation);
                digitalWrite(enablePin, LOW);
                digitalWrite(input1Pin, HIGH);
                digitalWrite(input2Pin, LOW);
                digitalWrite(enablePin, HIGH);
            }
            bit_array_pos++;
        }
    }

    Py_RETURN_NONE;
}

static PyObject * dcc_rpi_encoder_c_brake(PyObject *self, PyObject *args){
    const int brake;
    if (!PyArg_ParseTuple(args, "I", &brake))
        return NULL;

    if (brake == 0)
//        digitalWrite(brakePin, LOW);
        digitalWrite(enablePin, HIGH);
    else
//        digitalWrite(brakePin, HIGH);
        digitalWrite(enablePin, LOW);
    Py_RETURN_NONE;
}

static PyObject * dcc_rpi_encoder_c_setup(PyObject *self, PyObject *args){
    wiringPiSetup();
    pinMode(input1Pin, OUTPUT);
    pinMode(input2Pin, OUTPUT);
    pinMode(enablePin, OUTPUT);

    digitalWrite(input1Pin, HIGH);
    digitalWrite(input2Pin, LOW);
    digitalWrite(enablePin, LOW);

    Py_RETURN_NONE;
}

static PyObject * dcc_rpi_encoder_c_shutdown(PyObject *self, PyObject *args){

    digitalWrite(input1Pin, LOW);
    digitalWrite(input2Pin, LOW);
    digitalWrite(enablePin, LOW);

    Py_RETURN_NONE;
}



static PyMethodDef DCCRPiEncoderMethods[] = {
    {"send_bit_array", dcc_rpi_encoder_c_send_bit_array, METH_VARARGS,
     "Send some bits to the tracks"},
    {"brake", dcc_rpi_encoder_c_brake, METH_VARARGS,
     "Enable or disable a brake signal"},
    {"setup", dcc_rpi_encoder_c_setup, METH_VARARGS,
     "setup wiringPi and the default pins"},
    {"shutdown", dcc_rpi_encoder_c_shutdown, METH_VARARGS,
     "shutdown wiringPi and set all pins to LOW"},

    {NULL, NULL, 0, NULL} /* Sentinel - whatever that means */
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "dcc_rpi_encoder_c",  /* m_name */
    NULL,                 /* m_doc */
    -1,                   /* m_size */
    DCCRPiEncoderMethods, /* m_methods */
    NULL,                 /* m_reload */
    NULL,                 /* m_traverse */
    NULL,                 /* m_clear */
    NULL,                 /* m_free */
  };
#endif

static PyObject * moduleinit(void){
    PyObject *m;

#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&moduledef);
#else
    m = Py_InitModule("dcc_rpi_encoder_c", DCCRPiEncoderMethods);
#endif

    if (m == NULL)
        return NULL;

    return m;
}

#if PY_MAJOR_VERSION < 3
    PyMODINIT_FUNC initdcc_rpi_encoder_c(void){
        moduleinit();
    }
#else
    PyMODINIT_FUNC PyInit_dcc_rpi_encoder_c(void){
        return moduleinit();
    }
#endif
