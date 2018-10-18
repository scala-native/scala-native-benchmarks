package rsc

object RscBenchmark extends communitybench.Benchmark {
  def run(input: String): Int =
    rsc.cli.Main.run(input.split("\\s+"))

  override def main(args: Array[String]): Unit =
    super.main(args)
}
