import threading
import time
import random

class LaboratorioBasicoSinSync:
    def __init__(self, total_pcs):
        self.computadoras_disponibles = total_pcs

    def reservar_pc(self, usuario_id):
        if self.computadoras_disponibles > 0:
            time.sleep(0.001)
            self.computadoras_disponibles -= 1
            print(f"[BASICO SIN SYNC] Usuario {usuario_id} reservó PC. Disponibles: {self.computadoras_disponibles}")
            return True
        else:
            print(f"[BASICO SIN SYNC] Usuario {usuario_id} sin disponibilidad.")
            return False

    def liberar_pc(self, usuario_id):
        self.computadoras_disponibles += 1
        print(f"[BASICO SIN SYNC] Usuario {usuario_id} liberó PC. Disponibles: {self.computadoras_disponibles}")


class LaboratorioBasicoSincronizado:
    def __init__(self, total_pcs):
        self.computadoras_disponibles = total_pcs
        self.lock = threading.Lock()

    def reservar_pc(self, usuario_id):
        with self.lock:
            if self.computadoras_disponibles > 0:
                time.sleep(0.001)
                self.computadoras_disponibles -= 1
                print(f"[BASICO SINC] Usuario {usuario_id} reservó PC. Disponibles: {self.computadoras_disponibles}")
                return True
            else:
                print(f"[BASICO SINC] Usuario {usuario_id} sin disponibilidad.")
                return False

    def liberar_pc(self, usuario_id):
        with self.lock:
            self.computadoras_disponibles += 1
            print(f"[BASICO SINC] Usuario {usuario_id} liberó PC. Disponibles: {self.computadoras_disponibles}")


class LaboratorioManager:
    def __init__(self, lista_pcs):
        self.estado_computadoras = {
            pc: {"estado": "disponible", "usuario_id": None, "tiempo_inicio": None}
            for pc in lista_pcs
        }
        self.lock = threading.Lock()

    def asignar_computadora(self, usuario_id):
        with self.lock:
            for pc_id, datos in self.estado_computadoras.items():
                if datos["estado"] == "disponible":
                    time.sleep(0.001)
                    datos["estado"] = "ocupado"
                    datos["usuario_id"] = usuario_id
                    datos["tiempo_inicio"] = time.time()
                    print(f"[COMPLEJO SINC] Usuario {usuario_id} asignado a {pc_id}.")
                    return pc_id
        
        print(f"[COMPLEJO SINC] Usuario {usuario_id}: No hay estaciones libres.")
        return None

    def liberar_computadora(self, pc_id):
        with self.lock:
            if pc_id in self.estado_computadoras and self.estado_computadoras[pc_id]["estado"] == "ocupado":
                usuario_previo = self.estado_computadoras[pc_id]["usuario_id"]
                self.estado_computadoras[pc_id]["estado"] = "disponible"
                self.estado_computadoras[pc_id]["usuario_id"] = None
                self.estado_computadoras[pc_id]["tiempo_inicio"] = None
                print(f"[COMPLEJO SINC] Terminal {pc_id} liberada (usuario previo: {usuario_previo}).")
                return True
        return False


class UsuarioThread(threading.Thread):
    def __init__(self, usuario_id, gestor_lab, modo="complejo"):
        super().__init__()
        self.id_usuario = usuario_id
        self.gestor_lab = gestor_lab
        self.modo = modo

    def run(self):
        time.sleep(random.uniform(0.01, 0.03))
        
        if self.modo == "basico_sin" or self.modo == "basico_sinc":
            if self.gestor_lab.reservar_pc(self.id_usuario):
                time.sleep(0.05)
                self.gestor_lab.liberar_pc(self.id_usuario)
        elif self.modo == "complejo":
            pc_asignada = self.gestor_lab.asignar_computadora(self.id_usuario)
            if pc_asignada:
                time.sleep(0.05)
                self.gestor_lab.liberar_computadora(pc_asignada)


if __name__ == "__main__":
    print("="*60)
    print(" 1. PRUEBA BÁSICA - SIN SINCRONIZACIÓN")
    print("="*60)
    lab_sin_sync = LaboratorioBasicoSinSync(total_pcs=2)
    hilos_1 = [UsuarioThread(f"Est_{i}", lab_sin_sync, modo="basico_sin") for i in range(5)]
    for h in hilos_1: h.start()
    for h in hilos_1: h.join()

    print("\n" + "="*60)
    print(" 2. PRUEBA BÁSICA - SINCRONIZADA CON MUTEX (Lock)")
    print("="*60)
    lab_basico_sync = LaboratorioBasicoSincronizado(total_pcs=2)
    hilos_2 = [UsuarioThread(f"Est_{i}", lab_basico_sync, modo="basico_sinc") for i in range(5)]
    for h in hilos_2: h.start()
    for h in hilos_2: h.join()

    print("\n" + "="*60)
    print(" 3. PRUEBA COMPLEJA - SINCRONIZADA (Diccionario con Metadatos)")
    print("="*60)
    lab_complejo = LaboratorioManager(["PC_01", "PC_02"])
    hilos_3 = [UsuarioThread(f"Alumno_{i}", lab_complejo, modo="complejo") for i in range(5)]
    for h in hilos_3: h.start()
    for h in hilos_3: h.join()