def run(currentComp):
    for nodeType in ["VectorMotionBlur"]:
        for node in currentComp.GetToolList(False, nodeType).values():
            node.UseGPU = 0

if __name__ == "__main__":
    run()