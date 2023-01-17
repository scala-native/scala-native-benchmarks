package som

import scala.{Int, Unit}

class Random {
  private var seed = 74755

  def next(): Int = {
    seed = ((seed * 1309) + 13849) & 65535;
    seed
  }
}
