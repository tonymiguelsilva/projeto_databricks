import { describe, expect, test } from 'vitest';
import { calcularSimulacao } from './formatos';

describe('simulador de realocação', () => {
  test('reproduz o cenário COL0017 para PRJ-011', () => {
    expect(calcularSimulacao(37.7, 7530.8, 199.8, 57, 40)).toEqual({
      horasMensais: 150.8,
      ociosidadeEvitada: 30123.2,
      diasRecuperados: 19,
      mobilizacao: 7992,
      saldo: 22131.2,
    });
  });
});
