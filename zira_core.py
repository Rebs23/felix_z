import numpy as np
from scipy.fft import fft2, ifft2

class ZiraEngine:
    """
    ZiraEngine: Motor de Inteligencia Fotónica Resonante.
    Simula la propagación de luz y la interferencia no lineal para la toma de decisiones.
    """
    def __init__(self, size=96, wavelength=0.12, kerr_strength=12.0, saturation=2.0, noise_level=0.003):
        self.size = size
        self.wavelength = wavelength
        self.kerr_strength = kerr_strength
        self.saturation = saturation
        self.noise_level = noise_level
        self.rng = np.random.default_rng()

    def create_field(self, inputs=None):
        """
        Inicializa un campo complejo (campo de luz).
        inputs: lista de (x, y, amplitud) donde x, y están en [-1, 1].
        """
        x = np.linspace(-1, 1, self.size)
        X, Y = np.meshgrid(x, x)
        field = np.zeros((self.size, self.size), dtype=complex)
        
        if inputs is None:
            inputs = [(0, 0, 1.0)]
            
        for xi, yi, amp in inputs:
            # Generar haz gaussiano
            gaussian = np.exp(-((X - xi)**2 + (Y - yi)**2) / 0.05)
            # Fase coherente
            phase = np.exp(1j * 2 * np.pi * X / self.wavelength)
            field += amp * gaussian * phase
            
        return field

    def propagate(self, field, timesteps=10):
        """
        Simulación física: Propagación libre (FFT) + Interacción no lineal (Kerr).
        """
        target_energy = np.sum(np.abs(field)**2)
        current_field = field.copy()
        
        # Pre-calcular filtro de propagación
        kx = np.fft.fftfreq(self.size)[:, None]
        ky = np.fft.fftfreq(self.size)[None, :]
        k2 = kx**2 + ky**2
        prop_phase = np.exp(-1j * 2 * np.pi * self.wavelength * k2)

        for _ in range(timesteps):
            # Paso 1: Propagación lineal en el dominio de frecuencias
            k_space = fft2(current_field) * prop_phase
            linear_step = ifft2(k_space)
            
            # Paso 2: Interacción no lineal (Efecto Kerr - Auto-enfoque/Interferencia)
            intensity = np.abs(linear_step)**2
            # Saturación para estabilidad biológica/física
            non_linear_shift = intensity / (1 + intensity / self.saturation)
            current_field = linear_step * np.exp(1j * self.kerr_strength * non_linear_shift)
            
            # Paso 3: Ruido estocástico (Simula fluctuaciones térmicas)
            noise = self.noise_level * (self.rng.standard_normal(current_field.shape) + 
                                       1j * self.rng.standard_normal(current_field.shape))
            current_field += noise
            
            # Paso 4: Normalización (Homeostasis energética)
            energy = np.sum(np.abs(current_field)**2)
            if energy > 0:
                current_field *= np.sqrt(target_energy / energy)
                
        return current_field

    def solve_logic(self, amp_left, amp_right):
        """
        Compuerta lógica AND implementada mediante interferencia de luz.
        """
        inputs = [(-0.4, 0, amp_left), (0.4, 0, amp_right)]
        field = self.create_field(inputs)
        # La lógica emerge de la interacción durante la propagación
        result_field = self.propagate(field, timesteps=30)
        
        intensity = np.abs(result_field)**2
        h, w = intensity.shape
        
        # Umbral de detección dinámico
        max_i = np.max(intensity)
        thr = 0.2 * max_i if max_i > 0 else 0.1
        mask = (intensity > thr).astype(int)
        
        # Detección en regiones espaciales
        l_zone = np.mean(mask[h//4:3*h//4, w//8:3*w//8]) > 0.15
        r_zone = np.mean(mask[h//4:3*h//4, 5*w//8:7*w//8]) > 0.15
        
        return 1 if (l_zone and r_zone) else 0

    def supreme_queen_consensus(self, agent_votes):
        """
        Algoritmo de consenso SupremeQueen: estabilidad de señal sobre ruido.
        """
        if not agent_votes:
            return False, 0.0
        
        votes = np.array(agent_votes).astype(float)
        strength = np.mean(votes)
        
        # En Zira, el consenso requiere una masa crítica para 'resonar'
        is_coherent = strength > 0.5
        return is_coherent, strength

if __name__ == "__main__":
    zira = ZiraEngine()
    print("--- Zira Core Engine Test ---")
    print(f"Test AND (1,1): {zira.solve_logic(1,1)} (Esperado: 1)")
    print(f"Test AND (1,0): {zira.solve_logic(1,0)} (Esperado: 0)")
    
    votes = [1, 1, 0, 1]
    coherent, power = zira.supreme_queen_consensus(votes)
    print(f"Consenso SupremeQueen: {coherent} con potencia {power}")
