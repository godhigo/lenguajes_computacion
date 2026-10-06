#include <iostream>
#include <string>

using namespace std;

class Persona {
    public:
        string nombre;
        int edad;

        void saludar() {
            cout << "Hola mundo" << endl;
        }

        int suma(int a, int b) {
            return a + b;
        }
};

int main() {
    Persona daniel;
    daniel.nombre = "Paulo";
    daniel.edad = 46;
    cout << "Mi nombre es " << daniel.nombre << endl;
    cout << "Mi edad es de " << daniel.edad << " anios" << endl;
    daniel.saludar();
    cout << daniel.suma(2, 8) << endl;
    return 0;
}
